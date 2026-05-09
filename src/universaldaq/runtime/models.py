from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Deque, Generic, TypeVar

from universaldaq.adapters import AdapterPollResult
from universaldaq.common import EventTime

PayloadT = TypeVar('PayloadT')


@dataclass(frozen=True, slots=True, kw_only=True)
class QueuedItem(Generic[PayloadT]):
    enqueued_at: EventTime
    payload: PayloadT


@dataclass(slots=True)
class BoundedRecordQueue(Generic[PayloadT]):
    max_items: int
    items: Deque[QueuedItem[PayloadT]] = field(default_factory=deque)
    dropped_count: int = 0
    high_watermark: int = 0

    def __post_init__(self) -> None:
        if self.max_items <= 0:
            raise ValueError('max_items must be positive')

    def push(self, *, payload: PayloadT, enqueued_at: EventTime) -> None:
        if len(self.items) >= self.max_items:
            self.items.popleft()
            self.dropped_count += 1
        self.items.append(QueuedItem(enqueued_at=enqueued_at, payload=payload))
        self.high_watermark = max(self.high_watermark, len(self.items))

    def pop_oldest(self) -> QueuedItem[PayloadT] | None:
        if not self.items:
            return None
        return self.items.popleft()

    def peek_oldest(self) -> QueuedItem[PayloadT] | None:
        if not self.items:
            return None
        return self.items[0]

    def drain(self, *, max_items: int | None = None) -> list[QueuedItem[PayloadT]]:
        if max_items is None:
            max_items = len(self.items)
        rows: list[QueuedItem[PayloadT]] = []
        while self.items and len(rows) < max_items:
            rows.append(self.items.popleft())
        return rows

    @property
    def depth(self) -> int:
        return len(self.items)

    def max_age(self, *, now: EventTime) -> int:
        oldest = self.peek_oldest()
        if oldest is None:
            return 0
        return max(0, int(now) - int(oldest.enqueued_at))


@dataclass(frozen=True, slots=True, kw_only=True)
class AcquisitionBatch:
    adapter_id: str
    timestamp: EventTime
    poll_result: AdapterPollResult


@dataclass(frozen=True, slots=True, kw_only=True)
class JournalEntry:
    timestamp: EventTime
    record_type: str
    payload: dict[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class PersistedJournalEntry:
    schema_version: str
    session_id: str | None
    segment_id: str | None
    sequence_id: int
    monotonic_ns: int
    timestamp: EventTime
    record_type: str
    payload: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            'schema_version': self.schema_version,
            'session_id': self.session_id,
            'segment_id': self.segment_id,
            'sequence_id': self.sequence_id,
            'monotonic_ns': self.monotonic_ns,
            'timestamp': int(self.timestamp),
            'record_type': self.record_type,
            'payload': self.payload,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class JournalSegmentInfo:
    segment_id: str
    relative_path: str
    first_sequence_id: int | None
    last_sequence_id: int | None
    record_count: int
    closed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            'segment_id': self.segment_id,
            'relative_path': self.relative_path,
            'first_sequence_id': self.first_sequence_id,
            'last_sequence_id': self.last_sequence_id,
            'record_count': self.record_count,
            'closed': self.closed,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class JournalManifest:
    schema_version: str
    session_id: str
    segments: tuple[JournalSegmentInfo, ...]
    total_record_count: int
    last_sequence_id: int
    updated_at: int

    def as_dict(self) -> dict[str, object]:
        return {
            'schema_version': self.schema_version,
            'session_id': self.session_id,
            'segments': [segment.as_dict() for segment in self.segments],
            'total_record_count': self.total_record_count,
            'last_sequence_id': self.last_sequence_id,
            'updated_at': self.updated_at,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class PresentationSnapshot:
    published_at: EventTime
    lifecycle_phase: str
    active_adapter_id: str | None
    active_device_key: str | None
    changed_signal_count: int
    impacted_variable_count: int
    snapshot_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class VariableUpdateStats:
    changed_count: int
    transition_count: int
    skipped_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionCheckpoint:
    schema_version: str
    session_id: str
    checkpoint_id: str
    timestamp: EventTime
    last_committed_sequence_id: int
    state_hash: str
    payload: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            'schema_version': self.schema_version,
            'session_id': self.session_id,
            'checkpoint_id': self.checkpoint_id,
            'timestamp': int(self.timestamp),
            'last_committed_sequence_id': self.last_committed_sequence_id,
            'state_hash': self.state_hash,
            'payload': self.payload,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionCheckpointWriteResult:
    checkpoint: SessionCheckpoint
    file_path: Path | None
    latest_file_path: Path | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeStatus:
    acquisition_queue_depth: int
    acquisition_queue_dropped: int
    acquisition_queue_high_watermark: int
    acquisition_queue_max_age_ticks: int
    presentation_queue_depth: int
    presentation_queue_dropped: int
    presentation_queue_high_watermark: int
    presentation_queue_max_age_ticks: int
    presentation_publish_count: int
    presentation_coalesced_count: int
    recent_signal_count: int
    recent_sample_count: int
    recent_cycle_count: int
    recent_runtime_event_count: int
    recent_variable_count: int
    recent_variable_transition_count: int
    journal_queue_depth: int
    journal_queue_dropped: int
    journal_queue_max_age_ticks: int
    journal_write_count: int
    journal_flush_count: int
    journal_path: str | None
    journal_session_id: str | None = None
    journal_manifest_path: str | None = None
    journal_segment_count: int = 0
    journal_last_sequence_id: int = 0
    checkpoint_path: str | None = None
    checkpoint_last_sequence_id: int = 0

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class JournalWriteResult:
    written_count: int
    file_path: Path | None
    manifest_path: Path | None = None
    segment_count: int = 0
    last_sequence_id: int = 0
