from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Mapping, Sequence

from universaldaq.adapters import AdapterPollResult, PointSnapshot
from universaldaq.common import EventTime, NullMetrics, RuntimeMetricsStore
from universaldaq.signals import VariableEvaluationResult, VariableSnapshot
from universaldaq.ui.models import DeviceLifecycleSummary, VariableHealthSummary

from .models import (
    AcquisitionBatch,
    BoundedRecordQueue,
    JournalEntry,
    JournalManifest,
    JournalSegmentInfo,
    JournalWriteResult,
    PersistedJournalEntry,
    PresentationSnapshot,
    RuntimeStatus,
    SessionCheckpoint,
    SessionCheckpointWriteResult,
    VariableUpdateStats,
)

MetricsLike = RuntimeMetricsStore | NullMetrics
_JOURNAL_SCHEMA_VERSION = 'udq.runtime.journal.v2'
_CHECKPOINT_SCHEMA_VERSION = 'udq.runtime.checkpoint.v1'


def _display_path(path: Path | None) -> str | None:
    if path is None:
        return None
    parts = path.parts
    for marker in ('proof', 'runtime'):
        if marker in parts:
            index = max(i for i, item in enumerate(parts) if item == marker)
            return str(Path(*parts[index:]))
    return path.name


def _fsync_directory(path: Path) -> None:
    if os.name == 'nt':
        return
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + '.tmp')
    with temp_path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)
    _fsync_directory(path.parent)


def _hash_payload(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


@dataclass(slots=True)
class AppendOnlyJournalService:
    file_path: Path | None
    metrics: MetricsLike | RuntimeMetricsStore | None = None
    queue_max_items: int = 4096
    max_segment_records: int = 512
    session_root_path: Path | None = None
    session_id: str | None = None
    _queue: BoundedRecordQueue[PersistedJournalEntry] = field(init=False)
    write_count: int = 0
    flush_count: int = 0
    _next_sequence_id: int = 1
    _segment_index: int = 0
    _manifest: JournalManifest | None = None
    _manifest_path: Path | None = None
    _journal_dir: Path | None = None
    _use_session_layout: bool = False
    _legacy_mirror_path: Path | None = None

    def __post_init__(self) -> None:
        self._queue = BoundedRecordQueue[PersistedJournalEntry](max_items=self.queue_max_items)
        self.metrics = self.metrics if self.metrics is not None else NullMetrics()

    @property
    def queue_depth(self) -> int:
        return self._queue.depth

    @property
    def dropped_count(self) -> int:
        return self._queue.dropped_count

    @property
    def last_sequence_id(self) -> int:
        return self._next_sequence_id - 1

    @property
    def manifest_path(self) -> Path | None:
        return self._manifest_path

    @property
    def segment_count(self) -> int:
        return 0 if self._manifest is None else len(self._manifest.segments)

    def max_age(self, *, now: EventTime) -> int:
        return self._queue.max_age(now=now)

    def activate_session(self, *, session_id: str, session_root_path: Path | None = None) -> None:
        original_file_path = self.file_path
        self.session_id = session_id
        base_root = session_root_path or self.session_root_path
        if base_root is None:
            if self.file_path is not None:
                base_root = self.file_path.parent / 'sessions' / session_id
            else:
                base_root = Path(tempfile.gettempdir()) / 'universaldaq_runtime' / 'sessions' / session_id
        self.session_root_path = base_root
        self._journal_dir = self.session_root_path / 'journal'
        self._journal_dir.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._journal_dir / 'manifest.json'
        self._use_session_layout = True
        self._legacy_mirror_path = original_file_path
        self.file_path = self._journal_dir / 'segment-0001.jsonl'
        self._load_or_initialize_manifest()
        self.metrics.set_gauges({
            'runtime.journal.session_active': 1,
            'runtime.journal.segment.count': self.segment_count,
            'runtime.journal.last_sequence_id': self.last_sequence_id,
            'runtime.journal.manifest_path': '' if self._manifest_path is None else str(self._manifest_path),
        })

    def enqueue(self, *, entry: JournalEntry) -> None:
        queued = PersistedJournalEntry(
            schema_version=_JOURNAL_SCHEMA_VERSION,
            session_id=self.session_id,
            segment_id=None,
            sequence_id=self._next_sequence_id,
            monotonic_ns=time.monotonic_ns(),
            timestamp=entry.timestamp,
            record_type=entry.record_type,
            payload=dict(entry.payload),
        )
        self._next_sequence_id += 1
        self._queue.push(payload=queued, enqueued_at=entry.timestamp)
        self.metrics.increment('runtime.journal.enqueue.count')
        self.metrics.set_gauges({
            'runtime.journal.queue.depth': self._queue.depth,
            'runtime.journal.queue.dropped': self._queue.dropped_count,
            'runtime.journal.queue.max_age_ticks': self._queue.max_age(now=entry.timestamp),
            'runtime.journal.last_sequence_id': self.last_sequence_id,
        })

    def flush(self, *, max_items: int | None = None, now: EventTime | None = None, durable: bool = True) -> JournalWriteResult:
        drain_now = EventTime(0 if now is None else int(now))
        with self.metrics.measure('runtime.journal.flush.ms'):
            drained = self._queue.drain(max_items=max_items)
            if drained:
                if self._use_session_layout:
                    drained_payloads = tuple(row.payload for row in drained)
                    self._flush_to_session_segments(drained=drained_payloads, durable=durable, timestamp=drain_now)
                    if self._legacy_mirror_path is not None and self._legacy_mirror_path != self.file_path:
                        self._flush_to_legacy_file(drained=drained_payloads, durable=durable, target_path=self._legacy_mirror_path)
                elif self.file_path is not None:
                    self._flush_to_legacy_file(drained=tuple(row.payload for row in drained), durable=durable, target_path=self.file_path)
            self.write_count += len(drained)
            self.flush_count += 1
        self.metrics.increment('runtime.journal.flush.count')
        self.metrics.increment('runtime.journal.write.count', len(drained))
        self.metrics.set_gauges({
            'runtime.journal.queue.depth': self._queue.depth,
            'runtime.journal.queue.dropped': self._queue.dropped_count,
            'runtime.journal.queue.max_age_ticks': self._queue.max_age(now=drain_now),
            'runtime.journal.flush_total': self.flush_count,
            'runtime.journal.last_flush_written_count': len(drained),
            'runtime.journal.file_path': '' if self.file_path is None else str(self.file_path),
            'runtime.journal.manifest_path': '' if self._manifest_path is None else str(self._manifest_path),
            'runtime.journal.segment.count': self.segment_count,
            'runtime.journal.last_sequence_id': self.last_sequence_id,
        })
        return JournalWriteResult(
            written_count=len(drained),
            file_path=self.file_path,
            manifest_path=self._manifest_path,
            segment_count=self.segment_count,
            last_sequence_id=self.last_sequence_id,
        )

    def read_persisted_entries(self, *, after_sequence_id: int = 0, limit: int | None = None) -> tuple[dict[str, object], ...]:
        rows: list[dict[str, object]] = []
        if self._use_session_layout and self._manifest is not None and self._journal_dir is not None:
            for segment in self._manifest.segments:
                if segment.last_sequence_id is not None and segment.last_sequence_id <= after_sequence_id:
                    continue
                segment_path = self._journal_dir / segment.relative_path
                if not segment_path.exists():
                    continue
                for line in segment_path.read_text(encoding='utf-8').splitlines():
                    if not line.strip():
                        continue
                    payload = json.loads(line)
                    if int(payload.get('sequence_id', 0) or 0) <= after_sequence_id:
                        continue
                    rows.append(payload)
                    if limit is not None and len(rows) >= limit:
                        return tuple(rows)
            return tuple(rows)
        if self.file_path is None or not self.file_path.exists():
            return tuple()
        for line in self.file_path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            if int(payload.get('sequence_id', 0) or 0) <= after_sequence_id:
                continue
            rows.append(payload)
            if limit is not None and len(rows) >= limit:
                break
        return tuple(rows)

    def segment_index_rows(self) -> tuple[dict[str, object], ...]:
        if self._manifest is None:
            return tuple()
        rows: list[dict[str, object]] = []
        for ordinal, segment in enumerate(self._manifest.segments, start=1):
            segment_path = None if self._journal_dir is None else self._journal_dir / segment.relative_path
            rows.append(
                {
                    'segment_ordinal': ordinal,
                    'segment_id': segment.segment_id,
                    'relative_path': segment.relative_path,
                    'display_path': _display_path(segment_path),
                    'first_sequence_id': segment.first_sequence_id,
                    'last_sequence_id': segment.last_sequence_id,
                    'record_count': segment.record_count,
                    'closed': segment.closed,
                }
            )
        return tuple(rows)

    def _load_or_initialize_manifest(self) -> None:
        assert self._manifest_path is not None
        if self._manifest_path.exists():
            payload = json.loads(self._manifest_path.read_text(encoding='utf-8'))
            segments = tuple(
                JournalSegmentInfo(
                    segment_id=str(row.get('segment_id', 'segment-0001')),
                    relative_path=str(row.get('relative_path', 'segment-0001.jsonl')),
                    first_sequence_id=None if row.get('first_sequence_id') is None else int(row['first_sequence_id']),
                    last_sequence_id=None if row.get('last_sequence_id') is None else int(row['last_sequence_id']),
                    record_count=int(row.get('record_count', 0) or 0),
                    closed=bool(row.get('closed', False)),
                )
                for row in payload.get('segments', ())
            )
            self._manifest = JournalManifest(
                schema_version=str(payload.get('schema_version', _JOURNAL_SCHEMA_VERSION)),
                session_id=str(payload.get('session_id', self.session_id or 'runtime-session')),
                segments=segments,
                total_record_count=int(payload.get('total_record_count', 0) or 0),
                last_sequence_id=int(payload.get('last_sequence_id', 0) or 0),
                updated_at=int(payload.get('updated_at', 0) or 0),
            )
            self._next_sequence_id = self._manifest.last_sequence_id + 1
            self._segment_index = len(self._manifest.segments)
            if self._manifest.segments:
                last_segment = self._manifest.segments[-1]
                self.file_path = self._journal_dir / last_segment.relative_path
            return
        first_segment = JournalSegmentInfo(
            segment_id='segment-0001',
            relative_path='segment-0001.jsonl',
            first_sequence_id=None,
            last_sequence_id=None,
            record_count=0,
            closed=False,
        )
        self._manifest = JournalManifest(
            schema_version=_JOURNAL_SCHEMA_VERSION,
            session_id=self.session_id or 'runtime-session',
            segments=(first_segment,),
            total_record_count=0,
            last_sequence_id=0,
            updated_at=0,
        )
        self._segment_index = 1
        self.file_path = self._journal_dir / first_segment.relative_path
        _atomic_write_json(self._manifest_path, self._manifest.as_dict())

    def _flush_to_legacy_file(self, *, drained: Sequence[PersistedJournalEntry], durable: bool, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open('a', encoding='utf-8') as handle:
            for entry in drained:
                payload = {
                    'timestamp': int(entry.timestamp),
                    'record_type': entry.record_type,
                    'payload': entry.payload,
                }
                handle.write(json.dumps(payload, sort_keys=True) + '\n')
            handle.flush()
            if durable:
                os.fsync(handle.fileno())

    def _flush_to_session_segments(self, *, drained: Sequence[PersistedJournalEntry], durable: bool, timestamp: EventTime) -> None:
        assert self._manifest is not None
        assert self._journal_dir is not None
        assert self._manifest_path is not None
        segments = list(self._manifest.segments)
        for entry in drained:
            current_segment = segments[-1]
            if current_segment.record_count >= self.max_segment_records:
                segments[-1] = replace(current_segment, closed=True)
                self._segment_index += 1
                current_segment = JournalSegmentInfo(
                    segment_id=f'segment-{self._segment_index:04d}',
                    relative_path=f'segment-{self._segment_index:04d}.jsonl',
                    first_sequence_id=None,
                    last_sequence_id=None,
                    record_count=0,
                    closed=False,
                )
                segments.append(current_segment)
            segment_path = self._journal_dir / current_segment.relative_path
            persisted = replace(entry, segment_id=current_segment.segment_id)
            with segment_path.open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(persisted.as_dict(), sort_keys=True) + '\n')
                handle.flush()
                if durable:
                    os.fsync(handle.fileno())
            first_sequence_id = current_segment.first_sequence_id
            if first_sequence_id is None:
                first_sequence_id = persisted.sequence_id
            segments[-1] = replace(
                current_segment,
                first_sequence_id=first_sequence_id,
                last_sequence_id=persisted.sequence_id,
                record_count=current_segment.record_count + 1,
                closed=False,
            )
            self.file_path = segment_path
        total_record_count = sum(segment.record_count for segment in segments)
        last_sequence_id = 0 if not segments else int(segments[-1].last_sequence_id or 0)
        self._manifest = JournalManifest(
            schema_version=_JOURNAL_SCHEMA_VERSION,
            session_id=self.session_id or 'runtime-session',
            segments=tuple(segments),
            total_record_count=total_record_count,
            last_sequence_id=last_sequence_id,
            updated_at=int(timestamp),
        )
        _atomic_write_json(self._manifest_path, self._manifest.as_dict())


@dataclass(slots=True)
class SessionCheckpointService:
    root_path: Path | None
    metrics: MetricsLike | RuntimeMetricsStore | None = None
    session_root_path: Path | None = None
    session_id: str | None = None
    _checkpoint_dir: Path | None = None
    _latest_path: Path | None = None

    def __post_init__(self) -> None:
        self.metrics = self.metrics if self.metrics is not None else NullMetrics()

    def activate_session(self, *, session_id: str, session_root_path: Path | None = None) -> None:
        self.session_id = session_id
        self.session_root_path = session_root_path or self.root_path or (Path(tempfile.gettempdir()) / 'universaldaq_runtime' / 'sessions' / session_id)
        self._checkpoint_dir = self.session_root_path / 'checkpoints'
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._latest_path = self._checkpoint_dir / 'latest.json'
        self.metrics.set_gauges({
            'runtime.checkpoint.session_active': 1,
            'runtime.checkpoint.latest_path': '' if self._latest_path is None else str(self._latest_path),
        })

    def write_checkpoint(
        self,
        *,
        timestamp: EventTime,
        last_committed_sequence_id: int,
        payload: Mapping[str, object],
        checkpoint_id: str | None = None,
    ) -> SessionCheckpointWriteResult:
        if self.session_id is None:
            raise RuntimeError('session checkpoint service is not active for a session')
        assert self._checkpoint_dir is not None
        assert self._latest_path is not None
        resolved_checkpoint_id = checkpoint_id or f'CHK-{self.session_id}-{int(timestamp)}-{last_committed_sequence_id}'
        normalized_payload = {str(key): value for key, value in payload.items()}
        checkpoint = SessionCheckpoint(
            schema_version=_CHECKPOINT_SCHEMA_VERSION,
            session_id=self.session_id,
            checkpoint_id=resolved_checkpoint_id,
            timestamp=timestamp,
            last_committed_sequence_id=last_committed_sequence_id,
            state_hash=_hash_payload(normalized_payload),
            payload=normalized_payload,
        )
        file_path = self._checkpoint_dir / f'{resolved_checkpoint_id}.json'
        _atomic_write_json(file_path, checkpoint.as_dict())
        _atomic_write_json(self._latest_path, checkpoint.as_dict())
        self.metrics.increment('runtime.checkpoint.write.count')
        self.metrics.set_gauges({
            'runtime.checkpoint.last_sequence_id': last_committed_sequence_id,
            'runtime.checkpoint.latest_path': str(self._latest_path),
        })
        return SessionCheckpointWriteResult(checkpoint=checkpoint, file_path=file_path, latest_file_path=self._latest_path)

    def load_latest_valid_checkpoint(self) -> SessionCheckpoint | None:
        candidates: list[Path] = []
        if self._latest_path is not None and self._latest_path.exists():
            candidates.append(self._latest_path)
        if self._checkpoint_dir is not None and self._checkpoint_dir.exists():
            versioned = sorted(
                (path for path in self._checkpoint_dir.glob('CHK-*.json') if path.is_file()),
                key=lambda item: item.name,
                reverse=True,
            )
            candidates.extend(versioned)
        seen: set[Path] = set()
        for path in candidates:
            if path in seen:
                continue
            seen.add(path)
            try:
                payload = json.loads(path.read_text(encoding='utf-8'))
                checkpoint = SessionCheckpoint(
                    schema_version=str(payload.get('schema_version', _CHECKPOINT_SCHEMA_VERSION)),
                    session_id=str(payload['session_id']),
                    checkpoint_id=str(payload['checkpoint_id']),
                    timestamp=EventTime(int(payload['timestamp'])),
                    last_committed_sequence_id=int(payload.get('last_committed_sequence_id', 0) or 0),
                    state_hash=str(payload['state_hash']),
                    payload=dict(payload.get('payload', {})),
                )
                if checkpoint.state_hash != _hash_payload(checkpoint.payload):
                    continue
                self.metrics.increment('runtime.checkpoint.load.count')
                self.metrics.set_gauges({'runtime.checkpoint.last_sequence_id': checkpoint.last_committed_sequence_id})
                return checkpoint
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
        return None

    def checkpoint_rows(self) -> tuple[dict[str, object], ...]:
        if self._checkpoint_dir is None or not self._checkpoint_dir.exists():
            return tuple()
        rows: list[dict[str, object]] = []
        for path in sorted((item for item in self._checkpoint_dir.glob('CHK-*.json') if item.is_file()), key=lambda item: item.name):
            try:
                payload = json.loads(path.read_text(encoding='utf-8'))
                state_hash = str(payload['state_hash'])
                checkpoint_payload = dict(payload.get('payload', {}))
                rows.append(
                    {
                        'checkpoint_id': str(payload['checkpoint_id']),
                        'session_id': str(payload['session_id']),
                        'timestamp': int(payload['timestamp']),
                        'last_committed_sequence_id': int(payload.get('last_committed_sequence_id', 0) or 0),
                        'state_hash': state_hash,
                        'hash_valid': state_hash == _hash_payload(checkpoint_payload),
                        'display_path': _display_path(path),
                    }
                )
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                rows.append({'display_path': _display_path(path), 'hash_valid': False, 'parse_error': True})
        return tuple(rows)


class RuntimeQualityService:
    def __init__(
        self,
        *,
        metrics: RuntimeMetricsStore | None = None,
        acquisition_queue_max_items: int = 128,
        point_history_limit: int = 256,
        event_history_limit: int = 128,
        cycle_history_limit: int = 128,
        variable_history_limit: int = 128,
        presentation_interval_ticks: int = 1,
        presentation_queue_max_items: int = 32,
        presentation_history_limit: int = 32,
        journal_file_path: Path | None = None,
        journal_queue_max_items: int = 4096,
        journal_event_flush_threshold: int = 16,
        journal_max_segment_records: int = 512,
        session_id: str | None = None,
        auto_checkpoint_interval_cycles: int | None = 1,
    ) -> None:
        self.metrics: MetricsLike = metrics if metrics is not None else NullMetrics()
        self.acquisition_queue = BoundedRecordQueue[AcquisitionBatch](max_items=acquisition_queue_max_items)
        self.point_history_limit = point_history_limit
        self.event_history = deque(maxlen=event_history_limit)
        self.cycle_history = deque(maxlen=cycle_history_limit)
        self.variable_history = deque(maxlen=variable_history_limit)
        self.point_history: dict[str, deque[dict[str, object]]] = defaultdict(lambda: deque(maxlen=point_history_limit))
        self.presentation_interval_ticks = max(1, presentation_interval_ticks)
        self.presentation_queue = BoundedRecordQueue[PresentationSnapshot](max_items=presentation_queue_max_items)
        self.presentation_history = deque(maxlen=presentation_history_limit)
        self.last_presentation_timestamp: EventTime | None = None
        self.last_presentation_snapshot: PresentationSnapshot | None = None
        self.presentation_publish_count = 0
        self.presentation_coalesced_count = 0
        self.variable_transition_count = 0
        self._sample_count = 0
        self.journal_event_flush_threshold = max(1, journal_event_flush_threshold)
        if journal_file_path is None:
            runtime_root = Path(tempfile.gettempdir()) / 'universaldaq_runtime'
            journal_file_path = runtime_root / 'session_journal.jsonl'
        self._runtime_root = journal_file_path.parent
        self.journal = AppendOnlyJournalService(
            file_path=journal_file_path,
            metrics=self.metrics,
            queue_max_items=journal_queue_max_items,
            max_segment_records=journal_max_segment_records,
        )
        self.checkpoints = SessionCheckpointService(root_path=self._runtime_root, metrics=self.metrics)
        self.auto_checkpoint_interval_cycles = None if auto_checkpoint_interval_cycles is None else max(1, int(auto_checkpoint_interval_cycles))
        self._processed_cycle_count = 0
        if session_id is not None:
            self.activate_session(session_id=session_id)

    def activate_session(self, *, session_id: str) -> None:
        session_root = self._runtime_root / 'sessions' / session_id
        self.journal.activate_session(session_id=session_id, session_root_path=session_root)
        self.checkpoints.activate_session(session_id=session_id, session_root_path=session_root)

    def capture_acquisition(self, *, adapter_id: str, timestamp: EventTime, poll_result: AdapterPollResult) -> None:
        with self.metrics.measure('runtime.acquisition.capture.ms'):
            self.acquisition_queue.push(
                payload=AcquisitionBatch(adapter_id=adapter_id, timestamp=timestamp, poll_result=poll_result),
                enqueued_at=timestamp,
            )
            self._update_queue_metrics(now=timestamp)
            self.metrics.increment('runtime.acquisition.capture.count')
            self.metrics.increment('runtime.acquisition.snapshot.count', len(poll_result.snapshots))
            self.metrics.set_gauges({
                'runtime.acquisition.last_snapshot_count': len(poll_result.snapshots),
            })

    def record_variable_results(
        self,
        *,
        timestamp: EventTime,
        results: tuple[VariableEvaluationResult, ...],
        previous_snapshots: Mapping[str, VariableSnapshot] | None = None,
    ) -> VariableUpdateStats:
        previous = {} if previous_snapshots is None else dict(previous_snapshots)
        changed_count = 0
        transition_count = 0
        skipped_count = 0
        for result in results:
            snapshot = result.snapshot
            prior = previous.get(str(snapshot.variable_id)) or previous.get(snapshot.variable_id)
            changed = (
                prior is None
                or prior.value != snapshot.value
                or prior.quality != snapshot.quality
                or prior.state != snapshot.state
            )
            state_transition = prior is None or prior.state != snapshot.state or prior.quality != snapshot.quality
            if not changed:
                skipped_count += 1
                continue
            changed_count += 1
            transition_count += int(state_transition)
            payload = {
                'variable_id': str(snapshot.variable_id),
                'value': snapshot.value,
                'quality': snapshot.quality.value,
                'state': snapshot.state.value,
                'timestamp': int(snapshot.timestamp),
                'dependency_values': dict(snapshot.dependency_values),
                'missing_dependencies': list(result.missing_dependencies),
                'changed': True,
                'state_transition': state_transition,
            }
            self.variable_history.append(payload)
            self.journal.enqueue(entry=JournalEntry(timestamp=timestamp, record_type='variable_update', payload=payload))
        self.variable_transition_count += transition_count
        self.metrics.increment('runtime.variable.changed.count', changed_count)
        self.metrics.increment('runtime.variable.transition.count', transition_count)
        self.metrics.increment('runtime.variable.noop.count', skipped_count)
        self.metrics.set_gauges({
            'runtime.variable.recent_count': len(self.variable_history),
            'runtime.variable.transition_total': self.variable_transition_count,
            'runtime.variable.changed_last_count': changed_count,
            'runtime.variable.value_change_last_count': changed_count,
            'runtime.variable.state_transition_last_count': transition_count,
            'runtime.variable.skipped_last_count': skipped_count,
        })
        return VariableUpdateStats(changed_count=changed_count, transition_count=transition_count, skipped_count=skipped_count)

    def record_processed_cycle(
        self,
        *,
        timestamp: EventTime,
        lifecycle_summary: DeviceLifecycleSummary,
        variable_summary: VariableHealthSummary,
        changed_signal_ids: tuple[str, ...],
        poll_result: AdapterPollResult | None,
    ) -> None:
        with self.metrics.measure('runtime.processing.cycle.ms'):
            batch = self.acquisition_queue.pop_oldest()
            if batch is not None and batch.payload.adapter_id != lifecycle_summary.active_adapter_id:
                self.metrics.increment('runtime.acquisition.mismatched_adapter.count')
            if batch is not None:
                self._append_samples(batch.payload.poll_result.snapshots)
            elif poll_result is not None:
                self._append_samples(poll_result.snapshots)
            if poll_result is not None:
                self._queue_sample_entries(timestamp=timestamp, poll_result=poll_result)
            self._queue_cycle_entry(
                timestamp=timestamp,
                lifecycle_summary=lifecycle_summary,
                variable_summary=variable_summary,
                changed_signal_ids=changed_signal_ids,
            )
            self._stage_presentation_snapshot(
                timestamp=timestamp,
                lifecycle_summary=lifecycle_summary,
                variable_summary=variable_summary,
                changed_signal_ids=changed_signal_ids,
                snapshot_count=0 if poll_result is None else len(poll_result.snapshots),
            )
            self._publish_due_presentation(now=timestamp)
            self.flush_journal(now=timestamp)
            self._update_queue_metrics(now=timestamp)
            self._processed_cycle_count += 1
            if self.checkpoints.session_id is not None and self._checkpoint_due_for_cycle():
                self.write_checkpoint(timestamp=timestamp)
            self.metrics.increment('runtime.processing.cycle.count')
            self.metrics.set_gauges({
                'runtime.processing.changed_signal_count': len(changed_signal_ids),
                'runtime.processing.impacted_variable_count': variable_summary.impacted_count,
                'runtime.processing.skipped_variable_count': max(0, variable_summary.total_variable_count - variable_summary.impacted_count),
            })


    def _checkpoint_due_for_cycle(self) -> bool:
        if self.auto_checkpoint_interval_cycles is None:
            return False
        return self._processed_cycle_count % self.auto_checkpoint_interval_cycles == 0

    def record_operational_entry(
        self,
        *,
        timestamp: EventTime,
        record_type: str,
        payload: dict[str, object],
        flush: bool = False,
    ) -> None:
        normalized_payload = {str(key): value for key, value in payload.items()}
        self.event_history.append({'timestamp': int(timestamp), 'record_type': record_type, **normalized_payload})
        self.journal.enqueue(entry=JournalEntry(timestamp=timestamp, record_type=record_type, payload=normalized_payload))
        if flush or self.journal.queue_depth >= self.journal_event_flush_threshold:
            self.flush_journal(now=timestamp)
        self.metrics.increment('runtime.event.count')
        self.metrics.set_gauges({'runtime.event.recent_count': len(self.event_history)})

    def recent_event_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows = list(self.event_history)
        return tuple(rows[-max(1, limit):])

    def record_state_event(
        self,
        *,
        timestamp: EventTime,
        event_type: str,
        attributes: dict[str, object],
    ) -> None:
        payload = {
            'event_type': event_type,
            **{str(key): value for key, value in attributes.items()},
        }
        self.record_operational_entry(timestamp=timestamp, record_type='runtime_event', payload=payload, flush=False)

    def flush_journal(self, *, now: EventTime, max_items: int = 256) -> JournalWriteResult:
        return self.journal.flush(max_items=max_items, now=now, durable=True)

    def write_checkpoint(self, *, timestamp: EventTime, payload: Mapping[str, object] | None = None) -> SessionCheckpointWriteResult | None:
        if self.checkpoints.session_id is None:
            return None
        if self.journal.queue_depth > 0:
            self.flush_journal(now=timestamp)
        checkpoint_payload = dict(self.build_checkpoint_payload(timestamp=timestamp) if payload is None else payload)
        result = self.checkpoints.write_checkpoint(
            timestamp=timestamp,
            last_committed_sequence_id=self.journal.last_sequence_id,
            payload=checkpoint_payload,
        )
        self.metrics.set_gauges({
            'runtime.checkpoint.last_sequence_id': result.checkpoint.last_committed_sequence_id,
            'runtime.checkpoint.latest_path': '' if result.latest_file_path is None else str(result.latest_file_path),
        })
        return result

    def build_checkpoint_payload(self, *, timestamp: EventTime) -> dict[str, object]:
        runtime_status = self.snapshot(now=timestamp).as_dict()
        return {
            'runtime_status': runtime_status,
            'recent_runtime_event_rows': list(self.recent_event_rows(limit=32)),
            'recent_variable_rows': list(self.variable_rows(limit=32)),
            'recent_cycle_rows': list(list(self.cycle_history)[-32:]),
            'recent_signal_history': {key: list(rows) for key, rows in sorted(self.point_history.items())},
            'presentation_snapshot': None if self.last_presentation_snapshot is None else {
                'published_at': int(self.last_presentation_snapshot.published_at),
                'lifecycle_phase': self.last_presentation_snapshot.lifecycle_phase,
                'active_adapter_id': self.last_presentation_snapshot.active_adapter_id,
                'active_device_key': self.last_presentation_snapshot.active_device_key,
                'changed_signal_count': self.last_presentation_snapshot.changed_signal_count,
                'impacted_variable_count': self.last_presentation_snapshot.impacted_variable_count,
                'snapshot_count': self.last_presentation_snapshot.snapshot_count,
            },
        }

    def latest_checkpoint(self) -> SessionCheckpoint | None:
        return self.checkpoints.load_latest_valid_checkpoint()

    def checkpoint_rows(self) -> tuple[dict[str, object], ...]:
        return self.checkpoints.checkpoint_rows()

    def history_tier_summary(self) -> dict[str, object]:
        segment_rows = self.journal.segment_index_rows()
        checkpoint_rows = self.checkpoint_rows()
        return {
            'hot': {
                'recent_signal_count': len(self.point_history),
                'recent_sample_count': self._sample_count,
                'presentation_snapshot_available': self.last_presentation_snapshot is not None,
            },
            'warm': {
                'runtime_event_count': len(self.event_history),
                'variable_row_count': len(self.variable_history),
                'cycle_row_count': len(self.cycle_history),
            },
            'cold': {
                'segment_count': len(segment_rows),
                'persisted_record_count': sum(int(row.get('record_count', 0) or 0) for row in segment_rows),
                'checkpoint_count': len(checkpoint_rows),
            },
        }

    def session_artifact_inventory(self) -> dict[str, object]:
        return {
            'session_id': self.journal.session_id,
            'journal_manifest_path': _display_path(self.journal.manifest_path),
            'journal_latest_segment_path': _display_path(self.journal.file_path),
            'journal_legacy_mirror_path': _display_path(self.journal._legacy_mirror_path),
            'checkpoint_latest_path': _display_path(self.checkpoints._latest_path),
            'segment_rows': list(self.journal.segment_index_rows()),
            'checkpoint_rows': list(self.checkpoint_rows()),
        }

    def latest_checkpoint_summary(self) -> dict[str, object]:
        checkpoint = self.latest_checkpoint()
        checkpoint_rows = self.checkpoint_rows()
        valid_rows = [row for row in checkpoint_rows if bool(row.get('hash_valid'))]
        checkpoint_sequence_ids = [int(row.get('last_committed_sequence_id', 0) or 0) for row in valid_rows]
        if checkpoint is None:
            return {
                'checkpoint_available': False,
                'checkpoint_path': _display_path(self.checkpoints._latest_path),
                'last_committed_sequence_id': 0,
                'state_hash': None,
                'valid_checkpoint_count': len(valid_rows),
                'checkpoint_ladder': [],
                'checkpoint_spacing': {
                    'min_sequence_gap': None,
                    'max_sequence_gap': None,
                    'average_sequence_gap': None,
                },
            }
        return {
            'checkpoint_available': True,
            'checkpoint_path': _display_path(self.checkpoints._latest_path),
            'checkpoint_id': checkpoint.checkpoint_id,
            'last_committed_sequence_id': checkpoint.last_committed_sequence_id,
            'state_hash': checkpoint.state_hash,
            'timestamp': int(checkpoint.timestamp),
            'valid_checkpoint_count': len(valid_rows),
            'checkpoint_ladder': [dict(row) for row in valid_rows],
            'checkpoint_spacing': self._checkpoint_spacing_summary(checkpoint_sequence_ids),
        }


    def _checkpoint_spacing_summary(self, checkpoint_sequence_ids: Sequence[int]) -> dict[str, object]:
        if len(checkpoint_sequence_ids) < 2:
            return {
                'min_sequence_gap': None,
                'max_sequence_gap': None,
                'average_sequence_gap': None,
            }
        gaps = [
            max(0, int(right) - int(left))
            for left, right in zip(checkpoint_sequence_ids[:-1], checkpoint_sequence_ids[1:])
        ]
        return {
            'min_sequence_gap': min(gaps),
            'max_sequence_gap': max(gaps),
            'average_sequence_gap': sum(gaps) / len(gaps),
        }

    def build_replay_report(self, *, limit: int = 256) -> dict[str, object]:
        checkpoint = self.latest_checkpoint()
        if checkpoint is None:
            return {
                'checkpoint_available': False,
                'replay_state_hash': None,
                'tail_record_count': 0,
                'deterministic_replay': False,
                'segment_index': list(self.journal.segment_index_rows()),
            }
        journal_tail = self.journal.read_persisted_entries(after_sequence_id=checkpoint.last_committed_sequence_id, limit=limit)
        projected_state = self._project_replay_state(checkpoint=checkpoint, journal_tail=journal_tail)
        replay_state_hash = _hash_payload(projected_state)
        deterministic_input = {
            'checkpoint': checkpoint.as_dict(),
            'journal_tail': list(journal_tail),
            'projected_state': projected_state,
        }
        deterministic_hash = _hash_payload(deterministic_input)
        tail_record_counts_by_type = dict(projected_state.get('tail_record_counts_by_type', {}))
        tail_runtime_event_counts_by_type = dict(projected_state.get('tail_runtime_event_counts_by_type', {}))
        return {
            'checkpoint_available': True,
            'checkpoint_id': checkpoint.checkpoint_id,
            'last_committed_sequence_id': checkpoint.last_committed_sequence_id,
            'tail_record_count': len(journal_tail),
            'tail_first_sequence_id': None if not journal_tail else journal_tail[0].get('sequence_id'),
            'tail_last_sequence_id': None if not journal_tail else journal_tail[-1].get('sequence_id'),
            'tail_record_counts_by_type': tail_record_counts_by_type,
            'tail_runtime_event_counts_by_type': tail_runtime_event_counts_by_type,
            'tail_record_type_count': len(tail_record_counts_by_type),
            'tail_contains_multiple_record_types': len(tail_record_counts_by_type) > 1,
            'projected_state': projected_state,
            'replay_state_hash': replay_state_hash,
            'deterministic_input_hash': deterministic_hash,
            'deterministic_replay': True,
            'segment_index': list(self.journal.segment_index_rows()),
        }

    def build_recovery_bundle(self, *, limit: int = 256) -> dict[str, object]:
        checkpoint = self.latest_checkpoint()
        if checkpoint is None:
            return {
                'checkpoint_available': False,
                'journal_tail': (),
                'reconstructed_state_hash': None,
                'state_hash_matches': False,
                'segment_index': list(self.journal.segment_index_rows()),
                'history_tier_summary': self.history_tier_summary(),
                'artifact_inventory': self.session_artifact_inventory(),
                'replay_report': self.build_replay_report(limit=limit),
            }
        journal_tail = self.journal.read_persisted_entries(after_sequence_id=checkpoint.last_committed_sequence_id, limit=limit)
        reconstructed_state_hash = _hash_payload(checkpoint.payload)
        replay_report = self.build_replay_report(limit=limit)
        return {
            'checkpoint_available': True,
            'checkpoint': checkpoint.as_dict(),
            'journal_tail': journal_tail,
            'reconstructed_state_hash': reconstructed_state_hash,
            'state_hash_matches': reconstructed_state_hash == checkpoint.state_hash,
            'segment_index': list(self.journal.segment_index_rows()),
            'history_tier_summary': self.history_tier_summary(),
            'artifact_inventory': self.session_artifact_inventory(),
            'replay_report': replay_report,
        }

    def _project_replay_state(
        self,
        *,
        checkpoint: SessionCheckpoint,
        journal_tail: Sequence[dict[str, object]],
    ) -> dict[str, object]:
        record_counts: dict[str, int] = {}
        event_counts: dict[str, int] = {}
        last_runtime_event: dict[str, object] | None = None
        last_cycle: dict[str, object] | None = None
        last_samples_by_point: dict[str, dict[str, object]] = {}
        last_variables_by_id: dict[str, dict[str, object]] = {}
        for row in journal_tail:
            record_type = str(row.get('record_type', 'unknown'))
            record_counts[record_type] = record_counts.get(record_type, 0) + 1
            payload = row.get('payload', {})
            if not isinstance(payload, dict):
                continue
            if record_type == 'runtime_event':
                event_type = str(payload.get('event_type', 'unknown'))
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                last_runtime_event = payload
            elif record_type == 'cycle':
                last_cycle = payload
            elif record_type == 'sample':
                point_key = str(payload.get('point_key', payload.get('point_id', 'unknown')))
                last_samples_by_point[point_key] = payload
            elif record_type == 'variable_update':
                variable_id = str(payload.get('variable_id', 'unknown'))
                last_variables_by_id[variable_id] = payload
        projected_state = {
            'checkpoint_state_hash': checkpoint.state_hash,
            'tail_record_counts_by_type': dict(sorted(record_counts.items())),
            'tail_runtime_event_counts_by_type': dict(sorted(event_counts.items())),
            'tail_last_cycle': last_cycle,
            'tail_last_runtime_event': last_runtime_event,
            'tail_last_samples_by_point': dict(sorted(last_samples_by_point.items())),
            'tail_last_variables_by_id': dict(sorted(last_variables_by_id.items())),
            'tail_last_sequence_id': 0 if not journal_tail else int(journal_tail[-1].get('sequence_id', 0) or 0),
            'tail_record_count': len(journal_tail),
        }
        return projected_state

    def variable_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows = list(self.variable_history)
        return tuple(rows[-max(1, limit):])

    def recent_sample_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows: list[dict[str, object]] = []
        for point_key, history in sorted(self.point_history.items()):
            for sample in history:
                row = dict(sample)
                row['point_key'] = point_key
                rows.append(row)
        rows.sort(key=lambda row: (int(row.get('timestamp', 0) or 0), str(row.get('point_key', ''))))
        return tuple(rows[-max(1, limit):])

    def history_index_report(self) -> dict[str, object]:
        sample_counts_by_point = {
            point_key: len(history)
            for point_key, history in sorted(self.point_history.items())
        }
        runtime_event_counts_by_type: dict[str, int] = {}
        for row in self.event_history:
            event_type = str(row.get('event_type', row.get('record_type', 'unknown')))
            runtime_event_counts_by_type[event_type] = runtime_event_counts_by_type.get(event_type, 0) + 1
        cycle_counts_by_phase: dict[str, int] = {}
        for row in self.cycle_history:
            phase = str(row.get('phase', 'unknown'))
            cycle_counts_by_phase[phase] = cycle_counts_by_phase.get(phase, 0) + 1
        variable_ids = tuple(sorted({str(row.get('variable_id', 'unknown')) for row in self.variable_history}))
        sample_timestamps = [int(row.get('timestamp', 0) or 0) for history in self.point_history.values() for row in history]
        event_timestamps = [int(row.get('timestamp', 0) or 0) for row in self.event_history]
        cycle_timestamps = [int(row.get('timestamp', 0) or 0) for row in self.cycle_history]
        checkpoint_rows = self.checkpoint_rows()
        segment_rows = self.journal.segment_index_rows()
        combined = sample_timestamps + event_timestamps + cycle_timestamps
        return {
            'time_range': {
                'min_timestamp': None if not combined else min(combined),
                'max_timestamp': None if not combined else max(combined),
            },
            'sample_counts_by_point': sample_counts_by_point,
            'runtime_event_counts_by_type': dict(sorted(runtime_event_counts_by_type.items())),
            'cycle_counts_by_phase': dict(sorted(cycle_counts_by_phase.items())),
            'variable_ids': list(variable_ids),
            'valid_checkpoint_sequence_ids': [
                int(row.get('last_committed_sequence_id', 0) or 0)
                for row in checkpoint_rows
                if bool(row.get('hash_valid'))
            ],
            'segments': [dict(row) for row in segment_rows],
        }

    def build_review_summary(self, *, limit: int = 16) -> dict[str, object]:
        checkpoint_summary = self.latest_checkpoint_summary()
        replay_report = self.build_replay_report(limit=max(limit * 8, 64))
        history_summary = self.history_tier_summary()
        artifact_inventory = self.session_artifact_inventory()
        segment_rows = artifact_inventory['segment_rows']
        session_depth_summary = {
            'total_persisted_records': history_summary['cold']['persisted_record_count'],
            'segment_count': history_summary['cold']['segment_count'],
            'checkpoint_count': history_summary['cold']['checkpoint_count'],
            'valid_checkpoint_count': checkpoint_summary.get('valid_checkpoint_count', 0),
            'checkpoint_sequence_ids': [
                int(row.get('last_committed_sequence_id', 0) or 0)
                for row in checkpoint_summary.get('checkpoint_ladder', [])
            ],
            'segment_sequence_ranges': [
                {
                    'segment_id': row.get('segment_id'),
                    'first_sequence_id': row.get('first_sequence_id'),
                    'last_sequence_id': row.get('last_sequence_id'),
                    'record_count': row.get('record_count'),
                }
                for row in segment_rows
            ],
            'replay_tail_record_count': replay_report['tail_record_count'],
            'replay_tail_record_type_count': replay_report.get('tail_record_type_count', 0),
            'replay_tail_contains_multiple_record_types': replay_report.get('tail_contains_multiple_record_types', False),
        }
        return {
            'session_id': self.journal.session_id,
            'history_tier_summary': history_summary,
            'history_index_report': self.history_index_report(),
            'artifact_inventory': artifact_inventory,
            'checkpoint_summary': checkpoint_summary,
            'replay_report': replay_report,
            'session_depth_summary': session_depth_summary,
            'recent_sample_rows': list(self.recent_sample_rows(limit=limit)),
            'recent_variable_rows': list(self.variable_rows(limit=limit)),
            'recent_cycle_rows': list(list(self.cycle_history)[-max(1, limit):]),
            'recent_runtime_event_rows': list(self.recent_event_rows(limit=limit)),
        }

    def _append_samples(self, snapshots: tuple[PointSnapshot, ...]) -> None:
        for snapshot in snapshots:
            record = {
                'timestamp': int(snapshot.received_timestamp),
                'value': snapshot.engineering_value,
                'quality': snapshot.quality.value,
                'point_id': snapshot.point.point_id,
                'units': '' if snapshot.point.units is None else snapshot.point.units,
            }
            history = self.point_history[snapshot.point.stable_key]
            sample_was_evicted = len(history) >= self.point_history_limit
            history.append(record)
            if not sample_was_evicted:
                self._sample_count += 1
        self.metrics.set_gauges({
            'runtime.buffer.signal_count': len(self.point_history),
            'runtime.buffer.sample_count': self._sample_count,
        })

    def _queue_sample_entries(self, *, timestamp: EventTime, poll_result: AdapterPollResult) -> None:
        for snapshot in poll_result.snapshots:
            payload = {
                'adapter_id': poll_result.adapter_id,
                'point_key': snapshot.point.stable_key,
                'point_id': snapshot.point.point_id,
                'quality': snapshot.quality.value,
                'value': snapshot.engineering_value,
                'timestamp': int(snapshot.received_timestamp),
            }
            self.journal.enqueue(entry=JournalEntry(timestamp=timestamp, record_type='sample', payload=payload))

    def _queue_cycle_entry(
        self,
        *,
        timestamp: EventTime,
        lifecycle_summary: DeviceLifecycleSummary,
        variable_summary: VariableHealthSummary,
        changed_signal_ids: tuple[str, ...],
    ) -> None:
        payload = {
            'phase': lifecycle_summary.phase,
            'active_adapter_id': lifecycle_summary.active_adapter_id,
            'active_device_key': lifecycle_summary.active_device_key,
            'changed_signal_ids': list(changed_signal_ids),
            'changed_signal_count': len(changed_signal_ids),
            'impacted_variable_count': variable_summary.impacted_count,
            'total_variable_count': variable_summary.total_variable_count,
            'needs_review': lifecycle_summary.needs_review,
        }
        self.cycle_history.append(payload)
        self.journal.enqueue(entry=JournalEntry(timestamp=timestamp, record_type='cycle', payload=payload))
        self.metrics.set_gauges({'runtime.cycle.recent_count': len(self.cycle_history)})

    def _stage_presentation_snapshot(
        self,
        *,
        timestamp: EventTime,
        lifecycle_summary: DeviceLifecycleSummary,
        variable_summary: VariableHealthSummary,
        changed_signal_ids: tuple[str, ...],
        snapshot_count: int,
    ) -> None:
        snapshot = PresentationSnapshot(
            published_at=timestamp,
            lifecycle_phase=lifecycle_summary.phase,
            active_adapter_id=lifecycle_summary.active_adapter_id,
            active_device_key=lifecycle_summary.active_device_key,
            changed_signal_count=len(changed_signal_ids),
            impacted_variable_count=variable_summary.impacted_count,
            snapshot_count=snapshot_count,
        )
        self.presentation_queue.push(payload=snapshot, enqueued_at=timestamp)
        self.metrics.increment('runtime.presentation.stage.count')
        self.metrics.set_gauges({
            'runtime.presentation.queue.depth': self.presentation_queue.depth,
            'runtime.presentation.queue.dropped': self.presentation_queue.dropped_count,
            'runtime.presentation.queue.high_watermark': self.presentation_queue.high_watermark,
            'runtime.presentation.queue.max_age_ticks': self.presentation_queue.max_age(now=timestamp),
        })

    def _publish_due_presentation(self, *, now: EventTime) -> None:
        if self.presentation_queue.depth == 0:
            return
        should_publish = self.last_presentation_timestamp is None or (int(now) - int(self.last_presentation_timestamp)) >= self.presentation_interval_ticks
        if should_publish:
            drained = self.presentation_queue.drain()
            snapshot = drained[-1].payload
            self.presentation_history.append(snapshot)
            self.last_presentation_snapshot = snapshot
            self.last_presentation_timestamp = now
            self.presentation_publish_count += 1
            self.metrics.increment('runtime.presentation.publish.count')
        else:
            self.presentation_coalesced_count += 1
            self.metrics.increment('runtime.presentation.coalesced.count')
        self.metrics.set_gauges({
            'runtime.presentation.publish_total': self.presentation_publish_count,
            'runtime.presentation.coalesced_total': self.presentation_coalesced_count,
            'runtime.presentation.last_snapshot_count': 0 if self.last_presentation_snapshot is None else self.last_presentation_snapshot.snapshot_count,
            'runtime.presentation.last_changed_signal_count': 0 if self.last_presentation_snapshot is None else self.last_presentation_snapshot.changed_signal_count,
            'runtime.presentation.last_impacted_variable_count': 0 if self.last_presentation_snapshot is None else self.last_presentation_snapshot.impacted_variable_count,
            'runtime.presentation.queue.depth': self.presentation_queue.depth,
            'runtime.presentation.queue.dropped': self.presentation_queue.dropped_count,
            'runtime.presentation.queue.high_watermark': self.presentation_queue.high_watermark,
            'runtime.presentation.queue.max_age_ticks': self.presentation_queue.max_age(now=now),
        })

    def _update_queue_metrics(self, *, now: EventTime) -> None:
        self.metrics.set_gauges({
            'runtime.acquisition.queue.depth': self.acquisition_queue.depth,
            'runtime.acquisition.queue.dropped': self.acquisition_queue.dropped_count,
            'runtime.acquisition.queue.high_watermark': self.acquisition_queue.high_watermark,
            'runtime.acquisition.queue.max_age_ticks': self.acquisition_queue.max_age(now=now),
            'runtime.presentation.queue.depth': self.presentation_queue.depth,
            'runtime.presentation.queue.dropped': self.presentation_queue.dropped_count,
            'runtime.presentation.queue.high_watermark': self.presentation_queue.high_watermark,
            'runtime.presentation.queue.max_age_ticks': self.presentation_queue.max_age(now=now),
            'runtime.journal.queue.depth': self.journal.queue_depth,
            'runtime.journal.queue.dropped': self.journal.dropped_count,
            'runtime.journal.queue.max_age_ticks': self.journal.max_age(now=now),
            'runtime.journal.segment.count': self.journal.segment_count,
            'runtime.journal.last_sequence_id': self.journal.last_sequence_id,
        })

    def _recent_sample_count(self) -> int:
        return self._sample_count

    def snapshot(self, *, now: EventTime | None = None) -> RuntimeStatus:
        snapshot_now = EventTime(0 if now is None else int(now))
        if self.journal.queue_depth > 0:
            self.flush_journal(now=snapshot_now)
        checkpoint = self.latest_checkpoint()
        return RuntimeStatus(
            acquisition_queue_depth=self.acquisition_queue.depth,
            acquisition_queue_dropped=self.acquisition_queue.dropped_count,
            acquisition_queue_high_watermark=self.acquisition_queue.high_watermark,
            acquisition_queue_max_age_ticks=self.acquisition_queue.max_age(now=snapshot_now),
            presentation_queue_depth=self.presentation_queue.depth,
            presentation_queue_dropped=self.presentation_queue.dropped_count,
            presentation_queue_high_watermark=self.presentation_queue.high_watermark,
            presentation_queue_max_age_ticks=self.presentation_queue.max_age(now=snapshot_now),
            presentation_publish_count=self.presentation_publish_count,
            presentation_coalesced_count=self.presentation_coalesced_count,
            recent_signal_count=len(self.point_history),
            recent_sample_count=self._recent_sample_count(),
            recent_cycle_count=len(self.cycle_history),
            recent_runtime_event_count=len(self.event_history),
            recent_variable_count=len(self.variable_history),
            recent_variable_transition_count=self.variable_transition_count,
            journal_queue_depth=self.journal.queue_depth,
            journal_queue_dropped=self.journal.dropped_count,
            journal_queue_max_age_ticks=self.journal.max_age(now=snapshot_now),
            journal_write_count=self.journal.write_count,
            journal_flush_count=self.journal.flush_count,
            journal_path=_display_path(self.journal.file_path),
            journal_session_id=self.journal.session_id,
            journal_manifest_path=_display_path(self.journal.manifest_path),
            journal_segment_count=self.journal.segment_count,
            journal_last_sequence_id=self.journal.last_sequence_id,
            checkpoint_path=_display_path(self.checkpoints._latest_path),
            checkpoint_last_sequence_id=0 if checkpoint is None else checkpoint.last_committed_sequence_id,
        )
