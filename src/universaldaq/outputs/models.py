from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import TYPE_CHECKING, Mapping

from universaldaq.common import (
    ActorId,
    AuthorizationState,
    CommandDecision,
    EvidenceId,
    EvidenceKind,
    EvidenceRecord,
    EventTime,
    OutputId,
    RequestId,
)
from universaldaq.security import AuthorizationDecision

if TYPE_CHECKING:
    from universaldaq.adapters import AdapterCommandResult


@dataclass(frozen=True, slots=True, kw_only=True)
class OutputRequest:
    request_id: RequestId
    output_id: OutputId
    requested_value: str
    actor: ActorId
    requested_at: EventTime


@dataclass(frozen=True, slots=True, kw_only=True)
class OutputAppliedState:
    output_id: OutputId
    applied_value: str
    published_at: EventTime
    request_id: RequestId


@dataclass(frozen=True, slots=True, kw_only=True)
class OutputObservedState:
    output_id: OutputId
    observed_value: str
    observed_at: EventTime
    source: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OutputComparison:
    expected_value: str
    observed_value: str
    compared_at: EventTime

    @property
    def is_match(self) -> bool:
        return self.expected_value == self.observed_value


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandTrace:
    request: OutputRequest
    authorization_state: AuthorizationState
    decision: CommandDecision
    rejection_reason: str | None = None
    authorization_decision: AuthorizationDecision | None = None
    denial_reason_code: str | None = None
    rejection_phase: str | None = None
    applied_state: OutputAppliedState | None = None
    observed_state: OutputObservedState | None = None
    comparison: OutputComparison | None = None
    adapter_result: AdapterCommandResult | None = None
    evidence_records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)

    @property
    def apply_published(self) -> bool:
        return self.applied_state is not None

    @property
    def observed_mismatch(self) -> bool:
        return self.comparison is not None and not self.comparison.is_match

    @property
    def authorization_denied(self) -> bool:
        return self.authorization_state != AuthorizationState.ALLOWED and self.rejection_phase == 'authorization'

    @property
    def adapter_handoff_outcome(self) -> str | None:
        return None if self.adapter_result is None else self.adapter_result.outcome.value

    def with_adapter_result(self, adapter_result: AdapterCommandResult) -> 'CommandTrace':
        return replace(
            self,
            adapter_result=adapter_result,
            evidence_records=self.evidence_records + adapter_result.evidence_records(),
        )

    def export_rows(self) -> tuple[dict[str, str], ...]:
        rows = [
            {
                'record_type': 'command_trace',
                'request_id': str(self.request.request_id),
                'output_id': str(self.request.output_id),
                'actor': str(self.request.actor),
                'authorization_state': self.authorization_state.value,
                'decision': self.decision.value,
                'requested_at': str(self.request.requested_at),
                'requested_value': self.request.requested_value,
                'applied_value': '' if self.applied_state is None else self.applied_state.applied_value,
                'observed_value': '' if self.observed_state is None else self.observed_state.observed_value,
                'comparison_match': '' if self.comparison is None else str(self.comparison.is_match).lower(),
                'rejection_reason': '' if self.rejection_reason is None else self.rejection_reason,
                'denial_reason_code': '' if self.denial_reason_code is None else self.denial_reason_code,
                'rejection_phase': '' if self.rejection_phase is None else self.rejection_phase,
                'adapter_outcome': '' if self.adapter_result is None else self.adapter_result.outcome.value,
                'adapter_reason': '' if self.adapter_result is None or self.adapter_result.reason is None else self.adapter_result.reason,
                'adapter_id': '' if self.adapter_result is None else self.adapter_result.request.adapter_id,
                'adapter_point_id': '' if self.adapter_result is None else self.adapter_result.request.point_id,
            }
        ]
        if self.adapter_result is not None:
            rows.append(self.adapter_result.export_row())
        return tuple(rows)


class SafeStatePolicy(StrEnum):
    HOLD_LAST = 'hold_last'
    REJECT_COMMANDS = 'reject_commands'
    RETURN_TO_SAFE = 'return_to_safe'


@dataclass(frozen=True, slots=True, kw_only=True)
class WritableTagBinding:
    output_id: OutputId
    tag_key: str
    adapter_id: str
    point_id: str
    display_name: str
    safe_state_policy: SafeStatePolicy = SafeStatePolicy.REJECT_COMMANDS
    safe_state_value: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def export_row(self) -> dict[str, str]:
        return {
            'output_id': str(self.output_id),
            'tag_key': self.tag_key,
            'adapter_id': self.adapter_id,
            'point_id': self.point_id,
            'display_name': self.display_name,
            'safe_state_policy': self.safe_state_policy.value,
            'safe_state_value': '' if self.safe_state_value is None else self.safe_state_value,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class OwnershipLease:
    output_id: OutputId
    owner: ActorId
    acquired_at: EventTime
    expires_at: EventTime
    metadata: Mapping[str, str] = field(default_factory=dict)

    def is_active(self, *, timestamp: EventTime) -> bool:
        return int(timestamp) <= int(self.expires_at)

    def export_row(self) -> dict[str, str]:
        return {
            'output_id': str(self.output_id),
            'owner': str(self.owner),
            'acquired_at': str(self.acquired_at),
            'expires_at': str(self.expires_at),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class BrokerEvent:
    event_type: str
    output_id: OutputId
    timestamp: EventTime
    summary: str
    owner: ActorId | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def export_row(self) -> dict[str, str]:
        return {
            'event_type': self.event_type,
            'output_id': str(self.output_id),
            'timestamp': str(self.timestamp),
            'summary': self.summary,
            'owner': '' if self.owner is None else str(self.owner),
            **{f'metadata::{key}': value for key, value in self.metadata.items()},
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandExecutionResult:
    trace: CommandTrace
    disposition: str
    lease: OwnershipLease | None = None
    adapter_result: AdapterCommandResult | None = None
    broker_events: tuple[BrokerEvent, ...] = field(default_factory=tuple)

    @property
    def successful(self) -> bool:
        return self.adapter_result is not None and self.adapter_result.successful

    def export_row(self) -> dict[str, str]:
        return {
            'output_id': str(self.trace.request.output_id),
            'request_id': str(self.trace.request.request_id),
            'decision': self.trace.decision.value,
            'disposition': self.disposition,
            'owner': '' if self.lease is None else str(self.lease.owner),
            'lease_expires_at': '' if self.lease is None else str(self.lease.expires_at),
            'adapter_outcome': '' if self.adapter_result is None else self.adapter_result.outcome.value,
        }


class CommandTraceFactory:
    @staticmethod
    def _request_evidence(request: OutputRequest) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-{request.request_id}-REQ'),
            kind=EvidenceKind.EVENT,
            timestamp=request.requested_at,
            summary='request issued',
            attributes={'request_id': str(request.request_id), 'output_id': str(request.output_id)},
            source_kind='command_trace',
            source_id=str(request.request_id),
            actor_id=str(request.actor),
            tags=('commands',),
        )

    @staticmethod
    def authorization_denied(*, request: OutputRequest, decision: AuthorizationDecision) -> CommandTrace:
        evidence = (
            CommandTraceFactory._request_evidence(request),
            EvidenceRecord(
                evidence_id=EvidenceId(f'EVID-{request.request_id}-AUTHDENY'),
                kind=EvidenceKind.ASSERTION,
                timestamp=request.requested_at,
                summary='request denied by authorization policy',
                attributes={
                    'reason': decision.reason_text,
                    'reason_code': decision.reason_code.value,
                    'permission_family': decision.permission_family.value,
                    'apply_published': 'false',
                },
                source_kind='command_trace',
                source_id=str(request.request_id),
                session_id=decision.session_id,
                actor_id=str(decision.actor_id),
                origin=decision.origin,
                tags=('commands', 'authorization'),
            ),
        )
        return CommandTrace(
            request=request,
            authorization_state=decision.authorization_state,
            decision=CommandDecision.REJECTED,
            rejection_reason=decision.reason_text,
            authorization_decision=decision,
            denial_reason_code=decision.reason_code.value,
            rejection_phase='authorization',
            evidence_records=evidence,
        )

    @staticmethod
    def arbitration_blocked(
        *,
        request: OutputRequest,
        reason: str,
        authorization_state: AuthorizationState = AuthorizationState.ALLOWED,
        authorization_decision: AuthorizationDecision | None = None,
    ) -> CommandTrace:
        evidence = (
            CommandTraceFactory._request_evidence(request),
            EvidenceRecord(
                evidence_id=EvidenceId(f'EVID-{request.request_id}-REJECT'),
                kind=EvidenceKind.ASSERTION,
                timestamp=request.requested_at,
                summary='request blocked before apply',
                attributes={'reason': reason, 'apply_published': 'false'},
                source_kind='command_trace',
                source_id=str(request.request_id),
                actor_id=str(request.actor),
                tags=('commands',),
            ),
        )
        return CommandTrace(
            request=request,
            authorization_state=authorization_state,
            decision=CommandDecision.BLOCKED,
            rejection_reason=reason,
            authorization_decision=authorization_decision,
            rejection_phase='arbitration',
            evidence_records=evidence,
        )

    @staticmethod
    def blocked(*, request: OutputRequest, reason: str, authorization_state: AuthorizationState = AuthorizationState.ALLOWED) -> CommandTrace:
        return CommandTraceFactory.arbitration_blocked(
            request=request,
            reason=reason,
            authorization_state=authorization_state,
        )

    @staticmethod
    def applied_then_observed(
        *,
        request: OutputRequest,
        applied_value: str,
        observed_value: str,
        applied_at: EventTime,
        observed_at: EventTime,
        authorization_decision: AuthorizationDecision | None = None,
    ) -> CommandTrace:
        applied = OutputAppliedState(
            output_id=request.output_id,
            applied_value=applied_value,
            published_at=applied_at,
            request_id=request.request_id,
        )
        observed = OutputObservedState(
            output_id=request.output_id,
            observed_value=observed_value,
            observed_at=observed_at,
            source='feedback',
        )
        comparison = OutputComparison(expected_value=applied_value, observed_value=observed_value, compared_at=observed_at)
        summary = 'observed matches applied' if comparison.is_match else 'observed mismatch surfaced'
        evidence = (
            CommandTraceFactory._request_evidence(request),
            EvidenceRecord(
                evidence_id=EvidenceId(f'EVID-{request.request_id}-APPLY'),
                kind=EvidenceKind.TRACE,
                timestamp=applied_at,
                summary='apply published',
                attributes={'applied_value': applied_value},
                source_kind='command_trace',
                source_id=str(request.request_id),
                actor_id=str(request.actor),
                tags=('commands',),
            ),
            EvidenceRecord(
                evidence_id=EvidenceId(f'EVID-{request.request_id}-OBS'),
                kind=EvidenceKind.EVENT,
                timestamp=observed_at,
                summary=summary,
                attributes={
                    'observed_value': observed_value,
                    'expected_value': applied_value,
                    'is_match': str(comparison.is_match).lower(),
                },
                source_kind='command_trace',
                source_id=str(request.request_id),
                actor_id=str(request.actor),
                tags=('commands',),
            ),
        )
        return CommandTrace(
            request=request,
            authorization_state=AuthorizationState.ALLOWED,
            decision=CommandDecision.OBSERVED if comparison.is_match else CommandDecision.MISMATCHED,
            authorization_decision=authorization_decision,
            applied_state=applied,
            observed_state=observed,
            comparison=comparison,
            evidence_records=evidence,
        )
