from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

from universaldaq.common import ActorId, AuthorizationState, EvidenceId, EvidenceKind, EvidenceRecord, EventTime
from universaldaq.security import AuthorizationDecision


class CommandAdmissionStatus(StrEnum):
    ADMITTED = 'admitted'
    REJECTED = 'rejected'


class CommandDispatchStatus(StrEnum):
    NOT_DISPATCHED = 'not_dispatched'
    DRY_RUN_COMPLETED = 'dry_run_completed'
    COMPLETED = 'completed'
    FAILED = 'failed'


class CommandRejectionCode(StrEnum):
    AUTHORIZATION_DENIED = 'authorization_denied'
    INVALID_TARGET = 'invalid_target'
    UNSUPPORTED_CAPABILITY = 'unsupported_capability'
    STATE_GATE_FAILED = 'state_gate_failed'
    MALFORMED_PAYLOAD = 'malformed_payload'


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandIntent:
    command_id: str
    command_kind: str
    target_kind: str
    target_id: str
    requested_by: ActorId
    requested_at: EventTime
    correlation_id: str | None = None
    requested_payload: Mapping[str, object] = field(default_factory=dict)
    dry_run: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            'command_id': self.command_id,
            'command_kind': self.command_kind,
            'target_kind': self.target_kind,
            'target_id': self.target_id,
            'requested_by': str(self.requested_by),
            'requested_at': int(self.requested_at),
            'correlation_id': self.correlation_id,
            'requested_payload': {str(key): value for key, value in self.requested_payload.items()},
            'dry_run': self.dry_run,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandRecord:
    intent: CommandIntent
    admission_status: CommandAdmissionStatus
    authorization_state: AuthorizationState
    dispatch_status: CommandDispatchStatus
    result_summary: str
    governed_action: str | None = None
    rejection_code: CommandRejectionCode | None = None
    rejection_reason: str | None = None
    authorization_decision: AuthorizationDecision | None = None
    result_payload: Mapping[str, object] = field(default_factory=dict)
    evidence_records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)

    @property
    def admitted(self) -> bool:
        return self.admission_status == CommandAdmissionStatus.ADMITTED

    @property
    def rejected(self) -> bool:
        return self.admission_status == CommandAdmissionStatus.REJECTED

    def as_dict(self) -> dict[str, object]:
        return {
            'command_id': self.intent.command_id,
            'command_kind': self.intent.command_kind,
            'target_kind': self.intent.target_kind,
            'target_id': self.intent.target_id,
            'requested_by': str(self.intent.requested_by),
            'requested_at': int(self.intent.requested_at),
            'correlation_id': self.intent.correlation_id,
            'dry_run': self.intent.dry_run,
            'admission_status': self.admission_status.value,
            'authorization_state': self.authorization_state.value,
            'dispatch_status': self.dispatch_status.value,
            'result_summary': self.result_summary,
            'governed_action': self.governed_action,
            'rejection_code': None if self.rejection_code is None else self.rejection_code.value,
            'rejection_reason': self.rejection_reason,
            'result_payload': {str(key): value for key, value in self.result_payload.items()},
        }


class CommandRecordFactory:
    @staticmethod
    def _request_evidence(intent: CommandIntent) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-CMD-{intent.command_id}-REQ'),
            kind=EvidenceKind.EVENT,
            timestamp=intent.requested_at,
            summary='command requested',
            attributes={
                'command_id': intent.command_id,
                'command_kind': intent.command_kind,
                'target_kind': intent.target_kind,
                'target_id': intent.target_id,
                'dry_run': str(intent.dry_run).lower(),
            },
            source_kind='command_admission',
            source_id=intent.command_id,
            actor_id=str(intent.requested_by),
            tags=('commands',),
        )

    @staticmethod
    def rejected(
        *,
        intent: CommandIntent,
        authorization_state: AuthorizationState,
        rejection_code: CommandRejectionCode,
        rejection_reason: str,
        authorization_decision: AuthorizationDecision | None = None,
        governed_action: str | None = None,
        result_payload: Mapping[str, object] | None = None,
    ) -> CommandRecord:
        evidence = (
            CommandRecordFactory._request_evidence(intent),
            EvidenceRecord(
                evidence_id=EvidenceId(f'EVID-CMD-{intent.command_id}-REJECT'),
                kind=EvidenceKind.ASSERTION,
                timestamp=intent.requested_at,
                summary='command rejected',
                attributes={
                    'command_id': intent.command_id,
                    'rejection_code': rejection_code.value,
                    'rejection_reason': rejection_reason,
                },
                source_kind='command_admission',
                source_id=intent.command_id,
                actor_id=str(intent.requested_by),
                session_id=None if authorization_decision is None else authorization_decision.session_id,
                origin=None if authorization_decision is None else authorization_decision.origin,
                tags=('commands', 'rejected'),
            ),
        )
        return CommandRecord(
            intent=intent,
            admission_status=CommandAdmissionStatus.REJECTED,
            authorization_state=authorization_state,
            dispatch_status=CommandDispatchStatus.NOT_DISPATCHED,
            result_summary='command rejected',
            governed_action=governed_action,
            rejection_code=rejection_code,
            rejection_reason=rejection_reason,
            authorization_decision=authorization_decision,
            result_payload={} if result_payload is None else dict(result_payload),
            evidence_records=evidence,
        )

    @staticmethod
    def completed(
        *,
        intent: CommandIntent,
        authorization_state: AuthorizationState,
        dispatch_status: CommandDispatchStatus,
        result_summary: str,
        authorization_decision: AuthorizationDecision | None = None,
        governed_action: str | None = None,
        result_payload: Mapping[str, object] | None = None,
    ) -> CommandRecord:
        evidence = (
            CommandRecordFactory._request_evidence(intent),
            EvidenceRecord(
                evidence_id=EvidenceId(f'EVID-CMD-{intent.command_id}-ADMIT'),
                kind=EvidenceKind.ASSERTION,
                timestamp=intent.requested_at,
                summary='command admitted',
                attributes={
                    'command_id': intent.command_id,
                    'dispatch_status': dispatch_status.value,
                },
                source_kind='command_admission',
                source_id=intent.command_id,
                actor_id=str(intent.requested_by),
                session_id=None if authorization_decision is None else authorization_decision.session_id,
                origin=None if authorization_decision is None else authorization_decision.origin,
                tags=('commands', 'admitted'),
            ),
        )
        return CommandRecord(
            intent=intent,
            admission_status=CommandAdmissionStatus.ADMITTED,
            authorization_state=authorization_state,
            dispatch_status=dispatch_status,
            result_summary=result_summary,
            governed_action=governed_action,
            authorization_decision=authorization_decision,
            result_payload={} if result_payload is None else dict(result_payload),
            evidence_records=evidence,
        )
