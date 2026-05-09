from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable, Mapping
from uuid import uuid4

from universaldaq.common import EventTime


class MappingChangeKind(StrEnum):
    ADD = 'add'
    REMOVE = 'remove'
    REPLACE = 'replace'
    UNCHANGED = 'unchanged'
    INVALID = 'invalid'


class MappingPreflightSeverity(StrEnum):
    INFO = 'info'
    WARNING = 'warning'
    BLOCKING_ERROR = 'blocking_error'


class MappingPreflightState(StrEnum):
    PASS = 'pass'
    PASS_WITH_WARNINGS = 'pass_with_warnings'
    BLOCKED = 'blocked'
    STALE = 'stale'
    BACKEND_UNAVAILABLE = 'backend_unavailable'


class MappingApplyMode(StrEnum):
    DRY_RUN = 'dry_run'
    PREPARED_ONLY = 'prepared_only'


@dataclass(frozen=True, slots=True, kw_only=True)
class DraftBindingRow:
    """Shell draft row normalized for controller-facing preflight.

    This object is intentionally a draft/proposal carrier. It does not mutate or
    replace authoritative backend/controller readback state.
    """

    logical_id: str
    direction: str
    source_endpoint: str = ''
    destination_endpoint: str = ''
    logical_display_name: str = ''
    engineering_units: str | None = None
    device_identity_key: str = ''
    enabled: bool = True
    note: str = ''

    @property
    def binding_endpoint(self) -> str:
        if self.direction == 'internal_signal_to_device_output':
            return self.destination_endpoint
        return self.source_endpoint


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingChangeProposal:
    proposal_id: str
    change_kind: MappingChangeKind
    logical_id: str
    direction: str
    current_endpoint: str = ''
    proposed_endpoint: str = ''
    current_units: str | None = None
    proposed_units: str | None = None
    current_display_name: str = ''
    proposed_display_name: str = ''
    device_identity_key: str = ''
    authority_status: str = ''
    note: str = ''

    @property
    def is_noop(self) -> bool:
        return self.change_kind == MappingChangeKind.UNCHANGED

    @property
    def requires_preflight(self) -> bool:
        return self.change_kind in {
            MappingChangeKind.ADD,
            MappingChangeKind.REMOVE,
            MappingChangeKind.REPLACE,
            MappingChangeKind.INVALID,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingChangeSet:
    device_identity_key: str
    proposals: tuple[MappingChangeProposal, ...]
    authoritative_snapshot_timestamp: EventTime | None = None
    readback_available: bool = True
    authority_source: str = 'backend_controller_readback'

    @property
    def actionable_proposals(self) -> tuple[MappingChangeProposal, ...]:
        return tuple(proposal for proposal in self.proposals if proposal.requires_preflight)

    @property
    def change_count(self) -> int:
        return len(self.actionable_proposals)


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingPreflightIssue:
    severity: MappingPreflightSeverity
    code: str
    message: str
    proposal_id: str | None = None
    logical_id: str | None = None

    @property
    def blocks_request(self) -> bool:
        return self.severity == MappingPreflightSeverity.BLOCKING_ERROR


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingPreflightResult:
    change_set: MappingChangeSet
    state: MappingPreflightState
    issues: tuple[MappingPreflightIssue, ...] = field(default_factory=tuple)

    @property
    def blocking_issues(self) -> tuple[MappingPreflightIssue, ...]:
        return tuple(issue for issue in self.issues if issue.blocks_request)

    @property
    def warning_issues(self) -> tuple[MappingPreflightIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == MappingPreflightSeverity.WARNING)

    @property
    def can_prepare_apply_request(self) -> bool:
        return self.state in {MappingPreflightState.PASS, MappingPreflightState.PASS_WITH_WARNINGS} and not self.blocking_issues


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingReviewLine:
    proposal_id: str
    change_kind: str
    logical_id: str
    current_endpoint: str
    proposed_endpoint: str
    status_label: str
    message: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingReviewSummary:
    lines: tuple[MappingReviewLine, ...]
    preflight_state: str
    blocking_count: int = 0
    warning_count: int = 0

    @property
    def text(self) -> str:
        if not self.lines:
            return f'Mapping preflight: {self.preflight_state}; no actionable mapping changes.'
        rendered = [f'Mapping preflight: {self.preflight_state}']
        for index, line in enumerate(self.lines, start=1):
            rendered.append(
                f'{index}. {line.change_kind} {line.logical_id}: {line.current_endpoint or "<none>"} -> '
                f'{line.proposed_endpoint or "<none>"} [{line.status_label}] {line.message}'.strip()
            )
        return '\n'.join(rendered)


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingApplyRequest:
    request_id: str
    created_timestamp: EventTime
    mode: MappingApplyMode
    device_identity_key: str
    authoritative_snapshot_timestamp: EventTime | None
    proposals: tuple[MappingChangeProposal, ...]
    preflight_state: str
    review_summary: str
    requires_confirmation: bool = True
    executed: bool = False


def _value(row: Mapping[str, Any] | Any | None, key: str, default: str = '') -> str:
    if row is None:
        return default
    if isinstance(row, Mapping):
        return str(row.get(key, default) or default)
    return str(getattr(row, key, default) or default)


def _units(row: Mapping[str, Any] | Any | None) -> str | None:
    value = _value(row, 'engineering_units')
    return value or None


def _endpoint_for(*, direction: str, row: Mapping[str, Any] | Any | DraftBindingRow | None) -> str:
    if row is None:
        return ''
    if direction == 'internal_signal_to_device_output':
        return _value(row, 'destination_endpoint')
    return _value(row, 'source_endpoint')


def draft_binding_from_mapping_row(row: Any, *, device_identity_key: str = '') -> DraftBindingRow:
    return DraftBindingRow(
        logical_id=_value(row, 'row_id'),
        direction=_value(row, 'direction'),
        source_endpoint=_value(row, 'source_endpoint'),
        destination_endpoint=_value(row, 'destination_endpoint'),
        logical_display_name=_value(row, 'internal_signal_name'),
        engineering_units=_units(row),
        device_identity_key=device_identity_key,
        enabled=bool(getattr(row, 'enabled', True)),
        note=_value(row, 'note'),
    )


def _index_authoritative_rows(rows: Iterable[Mapping[str, Any] | Any]) -> dict[str, Mapping[str, Any] | Any]:
    indexed: dict[str, Mapping[str, Any] | Any] = {}
    for row in rows:
        logical_id = _value(row, 'logical_id')
        if logical_id:
            indexed[logical_id] = row
    return indexed


def _index_draft_rows(rows: Iterable[DraftBindingRow | Mapping[str, Any] | Any], *, device_identity_key: str) -> dict[str, DraftBindingRow]:
    indexed: dict[str, DraftBindingRow] = {}
    for row in rows:
        if isinstance(row, DraftBindingRow):
            draft = row
        else:
            draft = draft_binding_from_mapping_row(row, device_identity_key=device_identity_key)
        if draft.logical_id:
            indexed[draft.logical_id] = draft
    return indexed


def build_mapping_change_set(
    *,
    device_identity_key: str,
    authoritative_rows: Iterable[Mapping[str, Any] | Any],
    draft_rows: Iterable[DraftBindingRow | Mapping[str, Any] | Any],
    authoritative_snapshot_timestamp: EventTime | None = None,
    readback_available: bool = True,
    authority_source: str = 'backend_controller_readback',
) -> MappingChangeSet:
    authoritative_by_id = _index_authoritative_rows(authoritative_rows)
    draft_by_id = _index_draft_rows(draft_rows, device_identity_key=device_identity_key)
    proposals: list[MappingChangeProposal] = []
    all_ids = sorted(set(authoritative_by_id.keys()) | set(draft_by_id.keys()))
    for logical_id in all_ids:
        authority_row = authoritative_by_id.get(logical_id)
        draft_row = draft_by_id.get(logical_id)
        direction = _value(draft_row, 'direction') or _value(authority_row, 'direction')
        current_endpoint = _endpoint_for(direction=direction, row=authority_row)
        proposed_endpoint = _endpoint_for(direction=direction, row=draft_row)
        if authority_row is None and draft_row is not None:
            change_kind = MappingChangeKind.ADD
        elif authority_row is not None and draft_row is None:
            change_kind = MappingChangeKind.REMOVE
        elif not logical_id or not direction or (draft_row is not None and draft_row.enabled and not proposed_endpoint):
            change_kind = MappingChangeKind.INVALID
        elif current_endpoint == proposed_endpoint:
            change_kind = MappingChangeKind.UNCHANGED
        else:
            change_kind = MappingChangeKind.REPLACE
        proposals.append(
            MappingChangeProposal(
                proposal_id=f'map-proposal::{logical_id}',
                change_kind=change_kind,
                logical_id=logical_id,
                direction=direction,
                current_endpoint=current_endpoint,
                proposed_endpoint=proposed_endpoint,
                current_units=_units(authority_row),
                proposed_units=None if draft_row is None else draft_row.engineering_units,
                current_display_name=_value(authority_row, 'logical_display_name'),
                proposed_display_name='' if draft_row is None else draft_row.logical_display_name,
                device_identity_key=device_identity_key,
                authority_status=_value(authority_row, 'status'),
                note='prepared from authoritative readback and shell draft rows',
            )
        )
    return MappingChangeSet(
        device_identity_key=device_identity_key,
        proposals=tuple(proposals),
        authoritative_snapshot_timestamp=authoritative_snapshot_timestamp,
        readback_available=readback_available,
        authority_source=authority_source,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingPreflightValidator:
    known_signal_ids: frozenset[str] = frozenset()
    available_endpoints: frozenset[str] = frozenset()
    stale_statuses: frozenset[str] = frozenset({'stale', 'conflict', 'unavailable'})

    def validate(self, change_set: MappingChangeSet) -> MappingPreflightResult:
        issues: list[MappingPreflightIssue] = []
        if not change_set.readback_available:
            issues.append(
                MappingPreflightIssue(
                    severity=MappingPreflightSeverity.BLOCKING_ERROR,
                    code='BACKEND_UNAVAILABLE',
                    message='authoritative backend/controller readback is unavailable; mapping apply request cannot be prepared',
                )
            )
        if change_set.authoritative_snapshot_timestamp is None:
            issues.append(
                MappingPreflightIssue(
                    severity=MappingPreflightSeverity.BLOCKING_ERROR,
                    code='STALE_READBACK',
                    message='authoritative readback snapshot timestamp is missing; refresh readback before preparing an apply request',
                )
            )
        proposed_endpoint_counts: dict[tuple[str, str], int] = {}
        proposed_signal_counts: dict[str, int] = {}
        for proposal in change_set.actionable_proposals:
            if not proposal.logical_id:
                issues.append(self._block('MISSING_LOGICAL_ID', 'proposal is missing a logical signal/output ID', proposal))
            if not proposal.direction:
                issues.append(self._block('MISSING_DIRECTION', 'proposal is missing a mapping direction', proposal))
            if proposal.change_kind in {MappingChangeKind.ADD, MappingChangeKind.REPLACE, MappingChangeKind.INVALID} and not proposal.proposed_endpoint:
                issues.append(self._block('MISSING_ENDPOINT', 'proposal is missing the proposed device endpoint', proposal))
            if proposal.change_kind == MappingChangeKind.INVALID:
                issues.append(self._block('INVALID_PROPOSAL', 'proposal was classified as invalid before preflight', proposal))
            if self.known_signal_ids and proposal.logical_id not in self.known_signal_ids:
                issues.append(self._block('UNKNOWN_SIGNAL', 'target signal/output is not present in the known logical registry', proposal))
            if self.available_endpoints and proposal.proposed_endpoint and proposal.proposed_endpoint not in self.available_endpoints:
                issues.append(self._block('UNKNOWN_ENDPOINT', 'proposed endpoint is not present in the discovered device I/O inventory', proposal))
            if proposal.authority_status.lower() in self.stale_statuses:
                issues.append(self._block('STALE_AUTHORITY_ROW', 'authoritative row reports stale/conflict/unavailable status', proposal))
            if (
                proposal.current_units
                and proposal.proposed_units
                and proposal.current_units != proposal.proposed_units
                and proposal.change_kind in {MappingChangeKind.ADD, MappingChangeKind.REPLACE}
            ):
                issues.append(
                    MappingPreflightIssue(
                        severity=MappingPreflightSeverity.WARNING,
                        code='UNIT_MISMATCH',
                        message=f'current units {proposal.current_units!r} differ from proposed units {proposal.proposed_units!r}',
                        proposal_id=proposal.proposal_id,
                        logical_id=proposal.logical_id,
                    )
                )
            if proposal.change_kind in {MappingChangeKind.ADD, MappingChangeKind.REPLACE}:
                proposed_endpoint_counts[(proposal.direction, proposal.proposed_endpoint)] = proposed_endpoint_counts.get((proposal.direction, proposal.proposed_endpoint), 0) + 1
                proposed_signal_counts[proposal.logical_id] = proposed_signal_counts.get(proposal.logical_id, 0) + 1
        for (direction, endpoint), count in sorted(proposed_endpoint_counts.items()):
            if endpoint and count > 1:
                issues.append(
                    MappingPreflightIssue(
                        severity=MappingPreflightSeverity.BLOCKING_ERROR,
                        code='DUPLICATE_ENDPOINT',
                        message=f'endpoint {endpoint!r} is proposed for {count} {direction} bindings',
                    )
                )
        for logical_id, count in sorted(proposed_signal_counts.items()):
            if count > 1:
                issues.append(
                    MappingPreflightIssue(
                        severity=MappingPreflightSeverity.BLOCKING_ERROR,
                        code='DUPLICATE_LOGICAL_ID',
                        message=f'logical ID {logical_id!r} appears in {count} proposed bindings',
                        logical_id=logical_id,
                    )
                )
        if any(issue.code == 'BACKEND_UNAVAILABLE' for issue in issues):
            state = MappingPreflightState.BACKEND_UNAVAILABLE
        elif any(issue.code in {'STALE_READBACK', 'STALE_AUTHORITY_ROW'} for issue in issues if issue.blocks_request):
            state = MappingPreflightState.STALE
        elif any(issue.blocks_request for issue in issues):
            state = MappingPreflightState.BLOCKED
        elif any(issue.severity == MappingPreflightSeverity.WARNING for issue in issues):
            state = MappingPreflightState.PASS_WITH_WARNINGS
        else:
            state = MappingPreflightState.PASS
        return MappingPreflightResult(change_set=change_set, state=state, issues=tuple(issues))

    @staticmethod
    def _block(code: str, message: str, proposal: MappingChangeProposal) -> MappingPreflightIssue:
        return MappingPreflightIssue(
            severity=MappingPreflightSeverity.BLOCKING_ERROR,
            code=code,
            message=message,
            proposal_id=proposal.proposal_id,
            logical_id=proposal.logical_id,
        )


def build_mapping_review_summary(result: MappingPreflightResult) -> MappingReviewSummary:
    issues_by_proposal: dict[str, list[MappingPreflightIssue]] = {}
    for issue in result.issues:
        if issue.proposal_id:
            issues_by_proposal.setdefault(issue.proposal_id, []).append(issue)
    lines: list[MappingReviewLine] = []
    for proposal in result.change_set.actionable_proposals:
        proposal_issues = issues_by_proposal.get(proposal.proposal_id, [])
        if any(issue.blocks_request for issue in proposal_issues):
            status_label = 'blocked'
        elif any(issue.severity == MappingPreflightSeverity.WARNING for issue in proposal_issues):
            status_label = 'warning'
        else:
            status_label = 'pass'
        message = '; '.join(issue.message for issue in proposal_issues) or 'proposal is reviewable and non-executing'
        lines.append(
            MappingReviewLine(
                proposal_id=proposal.proposal_id,
                change_kind=proposal.change_kind.value,
                logical_id=proposal.logical_id,
                current_endpoint=proposal.current_endpoint,
                proposed_endpoint=proposal.proposed_endpoint,
                status_label=status_label,
                message=message,
            )
        )
    return MappingReviewSummary(
        lines=tuple(lines),
        preflight_state=result.state.value,
        blocking_count=len(result.blocking_issues),
        warning_count=len(result.warning_issues),
    )


def prepare_mapping_apply_request(
    *,
    preflight_result: MappingPreflightResult,
    mode: MappingApplyMode = MappingApplyMode.PREPARED_ONLY,
    created_timestamp: EventTime,
    request_id: str | None = None,
) -> MappingApplyRequest:
    if mode not in {MappingApplyMode.DRY_RUN, MappingApplyMode.PREPARED_ONLY}:
        raise ValueError('live mapping apply execution is not available in this preflight/review sprint')
    if not preflight_result.can_prepare_apply_request:
        raise ValueError('mapping apply request cannot be prepared from a blocking preflight result')
    review_summary = build_mapping_review_summary(preflight_result)
    return MappingApplyRequest(
        request_id=request_id or f'map-apply-request::{uuid4()}',
        created_timestamp=created_timestamp,
        mode=mode,
        device_identity_key=preflight_result.change_set.device_identity_key,
        authoritative_snapshot_timestamp=preflight_result.change_set.authoritative_snapshot_timestamp,
        proposals=preflight_result.change_set.actionable_proposals,
        preflight_state=preflight_result.state.value,
        review_summary=review_summary.text,
        requires_confirmation=True,
        executed=False,
    )


__all__ = [
    'DraftBindingRow',
    'MappingApplyMode',
    'MappingApplyRequest',
    'MappingChangeKind',
    'MappingChangeProposal',
    'MappingChangeSet',
    'MappingPreflightIssue',
    'MappingPreflightResult',
    'MappingPreflightSeverity',
    'MappingPreflightState',
    'MappingPreflightValidator',
    'MappingReviewLine',
    'MappingReviewSummary',
    'build_mapping_change_set',
    'build_mapping_review_summary',
    'draft_binding_from_mapping_row',
    'prepare_mapping_apply_request',
]
