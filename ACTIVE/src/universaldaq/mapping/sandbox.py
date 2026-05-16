from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import StrEnum
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4

from universaldaq.app.mapping_apply_preflight import (
    MappingApplyMode,
    MappingApplyRequest,
    MappingChangeKind,
    MappingChangeProposal,
    MappingChangeSet,
    MappingPreflightValidator,
    build_mapping_change_set,
    prepare_mapping_apply_request,
)
from universaldaq.common import EventTime, as_event_time


class MappingSandboxEventKind(StrEnum):
    SNAPSHOT_CREATED = 'snapshot_created'
    APPLY_ACCEPTED = 'apply_accepted'
    APPLY_REJECTED = 'apply_rejected'
    ROLLBACK_ACCEPTED = 'rollback_accepted'
    ROLLBACK_REJECTED = 'rollback_rejected'


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingBindingRecord:
    """One sandbox mapping row.

    These records intentionally represent sandbox state only. They are not live
    hardware configuration, and applying them never calls an adapter or output
    authority path.
    """

    logical_id: str
    direction: str
    endpoint: str
    display_name: str = ''
    units: str | None = None
    device_identity_key: str = ''
    enabled: bool = True
    note: str = ''

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(payload: Mapping[str, Any]) -> 'MappingBindingRecord':
        return MappingBindingRecord(
            logical_id=str(payload.get('logical_id', '')),
            direction=str(payload.get('direction', '')),
            endpoint=str(payload.get('endpoint', '')),
            display_name=str(payload.get('display_name', '')),
            units=None if payload.get('units') in {None, ''} else str(payload.get('units')),
            device_identity_key=str(payload.get('device_identity_key', '')),
            enabled=bool(payload.get('enabled', True)),
            note=str(payload.get('note', '')),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingSandboxAuditEvent:
    event_id: str
    event_kind: str
    timestamp: EventTime
    request_id: str | None = None
    rollback_token: str | None = None
    before_hash: str | None = None
    after_hash: str | None = None
    accepted: bool = False
    executed_live: bool = False
    message: str = ''

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload['timestamp'] = int(self.timestamp)
        return payload


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingSandboxState:
    sandbox_id: str
    device_identity_key: str
    bindings: tuple[MappingBindingRecord, ...] = ()
    revision: int = 0
    created_timestamp: EventTime = field(default_factory=lambda: as_event_time(0))
    updated_timestamp: EventTime = field(default_factory=lambda: as_event_time(0))
    notes: tuple[str, ...] = ()

    def binding_by_logical_id(self) -> dict[str, MappingBindingRecord]:
        return {binding.logical_id: binding for binding in self.bindings if binding.logical_id}

    def to_dict(self) -> dict[str, Any]:
        return {
            'sandbox_id': self.sandbox_id,
            'device_identity_key': self.device_identity_key,
            'revision': self.revision,
            'created_timestamp': int(self.created_timestamp),
            'updated_timestamp': int(self.updated_timestamp),
            'bindings': [binding.to_dict() for binding in self.bindings],
            'notes': list(self.notes),
        }

    @staticmethod
    def from_dict(payload: Mapping[str, Any]) -> 'MappingSandboxState':
        return MappingSandboxState(
            sandbox_id=str(payload.get('sandbox_id', 'mapping-sandbox')),
            device_identity_key=str(payload.get('device_identity_key', '')),
            revision=int(payload.get('revision', 0)),
            created_timestamp=as_event_time(int(payload.get('created_timestamp', 0))),
            updated_timestamp=as_event_time(int(payload.get('updated_timestamp', 0))),
            bindings=tuple(MappingBindingRecord.from_dict(item) for item in payload.get('bindings', ()) if isinstance(item, Mapping)),
            notes=tuple(str(item) for item in payload.get('notes', ())),
        )

    def state_hash(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingSandboxSnapshot:
    snapshot_id: str
    rollback_token: str
    state: MappingSandboxState
    state_hash: str
    created_timestamp: EventTime

    def to_dict(self) -> dict[str, Any]:
        return {
            'snapshot_id': self.snapshot_id,
            'rollback_token': self.rollback_token,
            'state_hash': self.state_hash,
            'created_timestamp': int(self.created_timestamp),
            'state': self.state.to_dict(),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingDiffEntry:
    logical_id: str
    change_kind: str
    before_endpoint: str = ''
    after_endpoint: str = ''
    before_units: str | None = None
    after_units: str | None = None
    before_display_name: str = ''
    after_display_name: str = ''
    direction: str = ''

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingDiffReport:
    before_hash: str
    after_hash: str
    entries: tuple[MappingDiffEntry, ...]
    added_count: int = 0
    removed_count: int = 0
    changed_count: int = 0
    unchanged_count: int = 0

    @property
    def total_change_count(self) -> int:
        return self.added_count + self.removed_count + self.changed_count

    def to_dict(self) -> dict[str, Any]:
        return {
            'before_hash': self.before_hash,
            'after_hash': self.after_hash,
            'added_count': self.added_count,
            'removed_count': self.removed_count,
            'changed_count': self.changed_count,
            'unchanged_count': self.unchanged_count,
            'total_change_count': self.total_change_count,
            'entries': [entry.to_dict() for entry in self.entries],
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingSandboxApplyResult:
    result_id: str
    request_id: str | None
    accepted: bool
    before_hash: str
    after_hash: str
    rollback_token: str | None
    applied_change_count: int
    rejected_change_count: int = 0
    warnings: tuple[str, ...] = ()
    blocked_reason: str = ''
    executed_live: bool = False
    diff_report: MappingDiffReport | None = None
    audit_event: MappingSandboxAuditEvent | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            'result_id': self.result_id,
            'request_id': self.request_id,
            'accepted': self.accepted,
            'before_hash': self.before_hash,
            'after_hash': self.after_hash,
            'rollback_token': self.rollback_token,
            'applied_change_count': self.applied_change_count,
            'rejected_change_count': self.rejected_change_count,
            'warnings': list(self.warnings),
            'blocked_reason': self.blocked_reason,
            'executed_live': self.executed_live,
            'diff_report': None if self.diff_report is None else self.diff_report.to_dict(),
            'audit_event': None if self.audit_event is None else self.audit_event.to_dict(),
        }


class MappingSandboxStateStore:
    """In-memory sandbox store with explicit rollback snapshots."""

    def __init__(self, *, state: MappingSandboxState) -> None:
        self._state = copy.deepcopy(state)
        self._snapshots: dict[str, MappingSandboxSnapshot] = {}
        self._events: list[MappingSandboxAuditEvent] = []

    @property
    def state(self) -> MappingSandboxState:
        return self._state

    @property
    def events(self) -> tuple[MappingSandboxAuditEvent, ...]:
        return tuple(self._events)

    def snapshot(self, *, timestamp: EventTime, rollback_token: str | None = None) -> MappingSandboxSnapshot:
        token = rollback_token or f'map-sandbox-rollback::{uuid4()}'
        snapshot = MappingSandboxSnapshot(
            snapshot_id=f'map-sandbox-snapshot::{uuid4()}',
            rollback_token=token,
            state=copy.deepcopy(self._state),
            state_hash=self._state.state_hash(),
            created_timestamp=timestamp,
        )
        self._snapshots[token] = snapshot
        self._events.append(
            MappingSandboxAuditEvent(
                event_id=f'map-sandbox-audit::{uuid4()}',
                event_kind=MappingSandboxEventKind.SNAPSHOT_CREATED.value,
                timestamp=timestamp,
                rollback_token=token,
                before_hash=snapshot.state_hash,
                after_hash=snapshot.state_hash,
                accepted=True,
                message='Sandbox snapshot captured for rollback; no live execution occurred.',
            )
        )
        return snapshot

    def replace_state(self, state: MappingSandboxState) -> None:
        self._state = copy.deepcopy(state)

    def rollback(self, *, rollback_token: str, timestamp: EventTime) -> MappingSandboxApplyResult:
        before_hash = self._state.state_hash()
        snapshot = self._snapshots.get(rollback_token)
        if snapshot is None:
            event = MappingSandboxAuditEvent(
                event_id=f'map-sandbox-audit::{uuid4()}',
                event_kind=MappingSandboxEventKind.ROLLBACK_REJECTED.value,
                timestamp=timestamp,
                rollback_token=rollback_token,
                before_hash=before_hash,
                after_hash=before_hash,
                accepted=False,
                message='Rollback token is unknown; sandbox state was not changed.',
            )
            self._events.append(event)
            return MappingSandboxApplyResult(
                result_id=f'map-sandbox-rollback::{uuid4()}',
                request_id=None,
                accepted=False,
                before_hash=before_hash,
                after_hash=before_hash,
                rollback_token=rollback_token,
                applied_change_count=0,
                blocked_reason='unknown rollback token',
                audit_event=event,
            )
        self._state = copy.deepcopy(snapshot.state)
        after_hash = self._state.state_hash()
        diff = diff_sandbox_states(snapshot.state, MappingSandboxState.from_dict({**snapshot.state.to_dict(), 'revision': snapshot.state.revision}))
        event = MappingSandboxAuditEvent(
            event_id=f'map-sandbox-audit::{uuid4()}',
            event_kind=MappingSandboxEventKind.ROLLBACK_ACCEPTED.value,
            timestamp=timestamp,
            rollback_token=rollback_token,
            before_hash=before_hash,
            after_hash=after_hash,
            accepted=True,
            message='Sandbox rollback accepted; live state and hardware remained untouched.',
        )
        self._events.append(event)
        return MappingSandboxApplyResult(
            result_id=f'map-sandbox-rollback::{uuid4()}',
            request_id=None,
            accepted=True,
            before_hash=before_hash,
            after_hash=after_hash,
            rollback_token=rollback_token,
            applied_change_count=1 if before_hash != after_hash else 0,
            diff_report=diff,
            audit_event=event,
        )


class MappingSandboxController:
    """Applies prepared mapping requests to sandbox state only."""

    allowed_modes: frozenset[MappingApplyMode] = frozenset({MappingApplyMode.PREPARED_ONLY, MappingApplyMode.DRY_RUN})

    def apply_to_sandbox(
        self,
        *,
        store: MappingSandboxStateStore,
        request: MappingApplyRequest,
        created_timestamp: EventTime,
        result_id: str | None = None,
    ) -> MappingSandboxApplyResult:
        before_state = store.state
        before_hash = before_state.state_hash()
        if request.mode not in self.allowed_modes:
            event = MappingSandboxAuditEvent(
                event_id=f'map-sandbox-audit::{uuid4()}',
                event_kind=MappingSandboxEventKind.APPLY_REJECTED.value,
                timestamp=created_timestamp,
                request_id=request.request_id,
                before_hash=before_hash,
                after_hash=before_hash,
                accepted=False,
                message='Sandbox apply rejected because the request mode is outside sandbox authority.',
            )
            return MappingSandboxApplyResult(
                result_id=result_id or f'map-sandbox-result::{uuid4()}',
                request_id=request.request_id,
                accepted=False,
                before_hash=before_hash,
                after_hash=before_hash,
                rollback_token=None,
                applied_change_count=0,
                rejected_change_count=len(request.proposals),
                blocked_reason='only prepared_only and dry_run requests can be applied to sandbox state',
                audit_event=event,
            )
        rollback_token = f'map-sandbox-rollback::{uuid4()}'
        store.snapshot(timestamp=created_timestamp, rollback_token=rollback_token)
        after_state = _apply_proposals_to_state(before_state, request.proposals, timestamp=created_timestamp)
        diff = diff_sandbox_states(before_state, after_state)
        store.replace_state(after_state)
        after_hash = after_state.state_hash()
        event = MappingSandboxAuditEvent(
            event_id=f'map-sandbox-audit::{uuid4()}',
            event_kind=MappingSandboxEventKind.APPLY_ACCEPTED.value,
            timestamp=created_timestamp,
            request_id=request.request_id,
            rollback_token=rollback_token,
            before_hash=before_hash,
            after_hash=after_hash,
            accepted=True,
            executed_live=False,
            message=f'Sandbox apply accepted for {diff.total_change_count} mapping change(s); no live execution occurred.',
        )
        store._events.append(event)
        return MappingSandboxApplyResult(
            result_id=result_id or f'map-sandbox-result::{uuid4()}',
            request_id=request.request_id,
            accepted=True,
            before_hash=before_hash,
            after_hash=after_hash,
            rollback_token=rollback_token,
            applied_change_count=diff.total_change_count,
            warnings=_extract_request_warnings(request),
            executed_live=False,
            diff_report=diff,
            audit_event=event,
        )


def _extract_request_warnings(request: MappingApplyRequest) -> tuple[str, ...]:
    return tuple(line for line in request.review_summary.splitlines() if 'warning' in line.lower())


def _binding_from_proposal(proposal: MappingChangeProposal, *, timestamp: EventTime) -> MappingBindingRecord:
    _ = timestamp
    return MappingBindingRecord(
        logical_id=proposal.logical_id,
        direction=proposal.direction,
        endpoint=proposal.proposed_endpoint,
        display_name=proposal.proposed_display_name or proposal.logical_id,
        units=proposal.proposed_units,
        device_identity_key=proposal.device_identity_key,
        enabled=True,
        note=f'sandbox-applied:{proposal.change_kind.value}',
    )


def _apply_proposals_to_state(
    state: MappingSandboxState,
    proposals: Iterable[MappingChangeProposal],
    *,
    timestamp: EventTime,
) -> MappingSandboxState:
    by_id = state.binding_by_logical_id()
    for proposal in proposals:
        if proposal.change_kind == MappingChangeKind.UNCHANGED:
            continue
        if proposal.change_kind == MappingChangeKind.REMOVE:
            by_id.pop(proposal.logical_id, None)
            continue
        if proposal.change_kind in {MappingChangeKind.ADD, MappingChangeKind.REPLACE}:
            by_id[proposal.logical_id] = _binding_from_proposal(proposal, timestamp=timestamp)
            continue
        if proposal.change_kind == MappingChangeKind.INVALID:
            continue
    return replace(
        state,
        bindings=tuple(by_id[key] for key in sorted(by_id)),
        revision=state.revision + 1,
        updated_timestamp=timestamp,
    )


def diff_sandbox_states(before: MappingSandboxState, after: MappingSandboxState) -> MappingDiffReport:
    before_rows = before.binding_by_logical_id()
    after_rows = after.binding_by_logical_id()
    logical_ids = sorted(set(before_rows) | set(after_rows))
    entries: list[MappingDiffEntry] = []
    added = removed = changed = unchanged = 0
    for logical_id in logical_ids:
        before_row = before_rows.get(logical_id)
        after_row = after_rows.get(logical_id)
        if before_row is None and after_row is not None:
            kind = 'add'
            added += 1
        elif before_row is not None and after_row is None:
            kind = 'remove'
            removed += 1
        elif before_row == after_row:
            kind = 'unchanged'
            unchanged += 1
        else:
            kind = 'replace'
            changed += 1
        entries.append(
            MappingDiffEntry(
                logical_id=logical_id,
                change_kind=kind,
                before_endpoint='' if before_row is None else before_row.endpoint,
                after_endpoint='' if after_row is None else after_row.endpoint,
                before_units=None if before_row is None else before_row.units,
                after_units=None if after_row is None else after_row.units,
                before_display_name='' if before_row is None else before_row.display_name,
                after_display_name='' if after_row is None else after_row.display_name,
                direction=(after_row.direction if after_row is not None else before_row.direction if before_row is not None else ''),
            )
        )
    return MappingDiffReport(
        before_hash=before.state_hash(),
        after_hash=after.state_hash(),
        entries=tuple(entries),
        added_count=added,
        removed_count=removed,
        changed_count=changed,
        unchanged_count=unchanged,
    )


def export_mapping_diff_markdown(report: MappingDiffReport) -> str:
    lines = [
        '# Mapping sandbox diff report',
        '',
        f'- Before hash: `{report.before_hash}`',
        f'- After hash: `{report.after_hash}`',
        f'- Added: {report.added_count}',
        f'- Removed: {report.removed_count}',
        f'- Changed: {report.changed_count}',
        f'- Unchanged: {report.unchanged_count}',
        '',
        '| Logical ID | Change | Before endpoint | After endpoint | Units |',
        '|---|---:|---|---|---|',
    ]
    for entry in report.entries:
        units = entry.after_units or entry.before_units or ''
        lines.append(
            f'| `{entry.logical_id}` | {entry.change_kind} | `{entry.before_endpoint or "<none>"}` | `{entry.after_endpoint or "<none>"}` | {units} |'
        )
    lines.append('')
    lines.append('Live state and hardware outputs are outside this sandbox report and were not mutated.')
    return '\n'.join(lines) + '\n'


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')


def build_demo_sandbox_state() -> MappingSandboxState:
    return MappingSandboxState(
        sandbox_id='demo-mapping-sandbox',
        device_identity_key='DEMO-DEVICE-001',
        created_timestamp=as_event_time(1000),
        updated_timestamp=as_event_time(1000),
        bindings=(
            MappingBindingRecord(
                logical_id='SIG-DEMO-TEMP',
                direction='device_input_to_internal_signal',
                endpoint='ANALOG_IN_0',
                display_name='demo_temperature_c',
                units='C',
                device_identity_key='DEMO-DEVICE-001',
            ),
            MappingBindingRecord(
                logical_id='SIG-DEMO-PRESSURE',
                direction='device_input_to_internal_signal',
                endpoint='ANALOG_IN_1',
                display_name='demo_pressure_bar',
                units='bar',
                device_identity_key='DEMO-DEVICE-001',
            ),
        ),
        notes=('Demo state for Sprint 1 sandbox-only mapping mutation proof.',),
    )


def build_demo_apply_request(*, timestamp: EventTime = as_event_time(1001)) -> MappingApplyRequest:
    authoritative_rows = (
        {
            'logical_id': 'SIG-DEMO-TEMP',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'ANALOG_IN_0',
            'destination_endpoint': '',
            'logical_display_name': 'demo_temperature_c',
            'engineering_units': 'C',
            'authority_status': 'applied',
        },
        {
            'logical_id': 'SIG-DEMO-PRESSURE',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'ANALOG_IN_1',
            'destination_endpoint': '',
            'logical_display_name': 'demo_pressure_bar',
            'engineering_units': 'bar',
            'authority_status': 'applied',
        },
    )
    draft_rows = (
        {
            'row_id': 'SIG-DEMO-TEMP',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'ANALOG_IN_2',
            'destination_endpoint': '',
            'internal_signal_name': 'demo_temperature_c',
            'engineering_units': 'C',
            'enabled': True,
            'note': 'Move temperature demo signal to ANALOG_IN_2 in sandbox only.',
        },
        {
            'row_id': 'SIG-DEMO-PRESSURE',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'ANALOG_IN_1',
            'destination_endpoint': '',
            'internal_signal_name': 'demo_pressure_bar',
            'engineering_units': 'bar',
            'enabled': True,
            'note': 'Leave pressure demo signal unchanged.',
        },
        {
            'row_id': 'SIG-DEMO-FLOW',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'ANALOG_IN_3',
            'destination_endpoint': '',
            'internal_signal_name': 'demo_flow_slpm',
            'engineering_units': 'slpm',
            'enabled': True,
            'note': 'Add flow demo signal in sandbox only.',
        },
    )
    change_set: MappingChangeSet = build_mapping_change_set(
        device_identity_key='DEMO-DEVICE-001',
        draft_rows=draft_rows,
        authoritative_rows=authoritative_rows,
        authoritative_snapshot_timestamp=timestamp,
    )
    preflight = MappingPreflightValidator(
        known_signal_ids=('SIG-DEMO-TEMP', 'SIG-DEMO-PRESSURE', 'SIG-DEMO-FLOW'),
        available_endpoints=('ANALOG_IN_0', 'ANALOG_IN_1', 'ANALOG_IN_2', 'ANALOG_IN_3'),
    ).validate(change_set)
    return prepare_mapping_apply_request(
        preflight_result=preflight,
        mode=MappingApplyMode.PREPARED_ONLY,
        created_timestamp=timestamp,
        request_id='REQ-DEMO-SANDBOX-MAPPING-001',
    )
