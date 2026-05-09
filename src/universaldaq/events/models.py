from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.common import AlarmId, ActorId, AlarmLifecycleState, EvidenceId, EvidenceKind, EvidenceRecord, EventTime, SignalQuality, VariableId
from universaldaq.security import AuthorizationDecision
from universaldaq.signals import VariableState


@dataclass(frozen=True, slots=True, kw_only=True)
class EventRecord:
    event_id: str
    event_type: str
    timestamp: EventTime
    severity: str
    summary: str
    source_kind: str
    source_id: str
    correlation_id: str | None = None
    alarm_id: AlarmId | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': int(self.timestamp),
            'severity': self.severity,
            'summary': self.summary,
            'source_kind': self.source_kind,
            'source_id': self.source_id,
            'correlation_id': self.correlation_id,
            'alarm_id': None if self.alarm_id is None else str(self.alarm_id),
            'attributes': {str(key): value for key, value in self.attributes.items()},
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class AlarmDefinition:
    alarm_id: AlarmId
    summary: str
    severity: str
    source_kind: str
    source_id: str
    variable_id: VariableId
    condition_kind: str
    comparison: str | None = None
    threshold: float | None = None
    trigger_states: tuple[VariableState, ...] = ()
    trigger_qualities: tuple[SignalQuality, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class AlarmStatus:
    alarm_id: AlarmId
    summary: str
    severity: str
    source_kind: str
    source_id: str
    active: bool
    acknowledged: bool
    first_raised_at: EventTime | None
    last_changed_at: EventTime | None
    last_cleared_at: EventTime | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            'alarm_id': str(self.alarm_id),
            'summary': self.summary,
            'severity': self.severity,
            'source_kind': self.source_kind,
            'source_id': self.source_id,
            'active': self.active,
            'acknowledged': self.acknowledged,
            'first_raised_at': None if self.first_raised_at is None else int(self.first_raised_at),
            'last_changed_at': None if self.last_changed_at is None else int(self.last_changed_at),
            'last_cleared_at': None if self.last_cleared_at is None else int(self.last_cleared_at),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class EventEvaluationResult:
    events: tuple[EventRecord, ...] = ()
    changed_alarm_ids: tuple[AlarmId, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class AlarmTransition:
    state: AlarmLifecycleState
    timestamp: EventTime
    actor: ActorId | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AlarmLifecycle:
    alarm_id: AlarmId
    transitions: tuple[AlarmTransition, ...] = field(default_factory=tuple)
    evidence_records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)

    def assert_alarm(self, timestamp: EventTime) -> 'AlarmLifecycle':
        transition = AlarmTransition(state=AlarmLifecycleState.ASSERTED, timestamp=timestamp)
        evidence = EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-{self.alarm_id}-ASSERT-{timestamp}'),
            kind=EvidenceKind.EVENT,
            timestamp=timestamp,
            summary='alarm asserted',
            attributes={'alarm_id': str(self.alarm_id)},
            source_kind='alarm_lifecycle',
            source_id=str(self.alarm_id),
            tags=('alarms',),
        )
        return AlarmLifecycle(alarm_id=self.alarm_id, transitions=self.transitions + (transition,), evidence_records=self.evidence_records + (evidence,))

    def acknowledge(self, actor: ActorId, timestamp: EventTime) -> 'AlarmLifecycle':
        transition = AlarmTransition(state=AlarmLifecycleState.ACKNOWLEDGED, timestamp=timestamp, actor=actor)
        evidence = EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-{self.alarm_id}-ACK-{timestamp}'),
            kind=EvidenceKind.EVENT,
            timestamp=timestamp,
            summary='alarm acknowledged',
            attributes={'alarm_id': str(self.alarm_id), 'actor': str(actor)},
            source_kind='alarm_lifecycle',
            source_id=str(self.alarm_id),
            actor_id=str(actor),
            tags=('alarms',),
        )
        return AlarmLifecycle(alarm_id=self.alarm_id, transitions=self.transitions + (transition,), evidence_records=self.evidence_records + (evidence,))

    def acknowledge_denied(self, decision: AuthorizationDecision, timestamp: EventTime) -> 'AlarmLifecycle':
        evidence = EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-{self.alarm_id}-ACKDENY-{timestamp}'),
            kind=EvidenceKind.ASSERTION,
            timestamp=timestamp,
            summary='alarm acknowledgment denied by authorization policy',
            attributes={
                'alarm_id': str(self.alarm_id),
                'actor': str(decision.actor_id),
                'reason_code': decision.reason_code.value,
                'reason': decision.reason_text,
            },
            source_kind='alarm_lifecycle',
            source_id=str(self.alarm_id),
            actor_id=str(decision.actor_id),
            session_id=decision.session_id,
            origin=decision.origin,
            tags=('alarms', 'authorization'),
        )
        return AlarmLifecycle(alarm_id=self.alarm_id, transitions=self.transitions, evidence_records=self.evidence_records + (evidence,))

    def return_to_normal(self, timestamp: EventTime) -> 'AlarmLifecycle':
        transition = AlarmTransition(state=AlarmLifecycleState.RETURNED_TO_NORMAL, timestamp=timestamp)
        evidence = EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-{self.alarm_id}-RTN-{timestamp}'),
            kind=EvidenceKind.EVENT,
            timestamp=timestamp,
            summary='alarm returned to normal',
            attributes={'alarm_id': str(self.alarm_id)},
            source_kind='alarm_lifecycle',
            source_id=str(self.alarm_id),
            tags=('alarms',),
        )
        return AlarmLifecycle(alarm_id=self.alarm_id, transitions=self.transitions + (transition,), evidence_records=self.evidence_records + (evidence,))

    @property
    def ordered_states(self) -> tuple[AlarmLifecycleState, ...]:
        return tuple(item.state for item in self.transitions)

    def export_rows(self) -> tuple[dict[str, str], ...]:
        rows: list[dict[str, str]] = []
        for transition in self.transitions:
            rows.append(
                {
                    'record_type': 'alarm_transition',
                    'alarm_id': str(self.alarm_id),
                    'state': transition.state.value,
                    'timestamp': str(transition.timestamp),
                    'actor': '' if transition.actor is None else str(transition.actor),
                }
            )
        return tuple(rows)
