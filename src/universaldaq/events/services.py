from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.common import ActorId, AlarmId, EventTime, SignalQuality
from universaldaq.security import AuthorizationDecision
from universaldaq.signals import VariableSnapshot, VariableState

from .models import AlarmDefinition, AlarmLifecycle, AlarmStatus, EventEvaluationResult, EventRecord


@dataclass(slots=True)
class AlarmLifecycleService:
    lifecycles: dict[AlarmId, AlarmLifecycle] = field(default_factory=dict)
    definitions: dict[AlarmId, AlarmDefinition] = field(default_factory=dict)
    active_statuses: dict[AlarmId, AlarmStatus] = field(default_factory=dict)
    recent_events: deque[EventRecord] = field(default_factory=lambda: deque(maxlen=64))

    def register_alarm_definition(self, definition: AlarmDefinition) -> None:
        self.definitions[definition.alarm_id] = definition

    def assert_alarm(self, alarm_id: AlarmId, timestamp: EventTime) -> AlarmLifecycle:
        lifecycle = self.lifecycles.get(alarm_id, AlarmLifecycle(alarm_id=alarm_id)).assert_alarm(timestamp)
        self.lifecycles[alarm_id] = lifecycle
        definition = self.definitions.get(alarm_id)
        if definition is not None:
            self.active_statuses[alarm_id] = AlarmStatus(
                alarm_id=alarm_id,
                summary=definition.summary,
                severity=definition.severity,
                source_kind=definition.source_kind,
                source_id=definition.source_id,
                active=True,
                acknowledged=False,
                first_raised_at=timestamp if alarm_id not in self.active_statuses else self.active_statuses[alarm_id].first_raised_at,
                last_changed_at=timestamp,
                last_cleared_at=None,
            )
        return lifecycle

    def acknowledge(
        self,
        alarm_id: AlarmId,
        actor: ActorId,
        timestamp: EventTime,
        authorization_decision: AuthorizationDecision | None = None,
    ) -> AlarmLifecycle:
        lifecycle = self.lifecycles.get(alarm_id, AlarmLifecycle(alarm_id=alarm_id))
        if authorization_decision is not None and not authorization_decision.allowed:
            lifecycle = lifecycle.acknowledge_denied(authorization_decision, timestamp)
        else:
            lifecycle = lifecycle.acknowledge(actor, timestamp)
            status = self.active_statuses.get(alarm_id)
            if status is not None:
                self.active_statuses[alarm_id] = AlarmStatus(
                    alarm_id=status.alarm_id,
                    summary=status.summary,
                    severity=status.severity,
                    source_kind=status.source_kind,
                    source_id=status.source_id,
                    active=status.active,
                    acknowledged=True,
                    first_raised_at=status.first_raised_at,
                    last_changed_at=timestamp,
                    last_cleared_at=status.last_cleared_at,
                )
        self.lifecycles[alarm_id] = lifecycle
        return lifecycle

    def return_to_normal(self, alarm_id: AlarmId, timestamp: EventTime) -> AlarmLifecycle:
        lifecycle = self.lifecycles.get(alarm_id, AlarmLifecycle(alarm_id=alarm_id)).return_to_normal(timestamp)
        self.lifecycles[alarm_id] = lifecycle
        status = self.active_statuses.get(alarm_id)
        if status is not None:
            self.active_statuses[alarm_id] = AlarmStatus(
                alarm_id=status.alarm_id,
                summary=status.summary,
                severity=status.severity,
                source_kind=status.source_kind,
                source_id=status.source_id,
                active=False,
                acknowledged=status.acknowledged,
                first_raised_at=status.first_raised_at,
                last_changed_at=timestamp,
                last_cleared_at=timestamp,
            )
        return lifecycle

    def evaluate_variable_snapshots(
        self,
        *,
        timestamp: EventTime,
        snapshots: Mapping[object, VariableSnapshot],
    ) -> EventEvaluationResult:
        events: list[EventRecord] = []
        changed_alarm_ids: list[AlarmId] = []
        normalized_snapshots = {str(key): value for key, value in snapshots.items()}
        for definition in self.definitions.values():
            snapshot = normalized_snapshots.get(str(definition.variable_id))
            condition_active = self._condition_is_active(definition=definition, snapshot=snapshot)
            status = self.active_statuses.get(definition.alarm_id)
            is_currently_active = status is not None and status.active
            if condition_active and not is_currently_active:
                lifecycle = self.assert_alarm(definition.alarm_id, timestamp)
                changed_alarm_ids.append(definition.alarm_id)
                events.append(
                    self._append_event(
                        event=EventRecord(
                            event_id=f'EVT-{definition.alarm_id}-ASSERT-{int(timestamp)}',
                            event_type='alarm_raised',
                            timestamp=timestamp,
                            severity=definition.severity,
                            summary=definition.summary,
                            source_kind=definition.source_kind,
                            source_id=definition.source_id,
                            alarm_id=definition.alarm_id,
                            attributes=self._event_attributes(definition=definition, snapshot=snapshot, lifecycle=lifecycle, acknowledged=False),
                        )
                    )
                )
            elif (not condition_active) and is_currently_active:
                lifecycle = self.return_to_normal(definition.alarm_id, timestamp)
                changed_alarm_ids.append(definition.alarm_id)
                acknowledged = False if status is None else status.acknowledged
                events.append(
                    self._append_event(
                        event=EventRecord(
                            event_id=f'EVT-{definition.alarm_id}-CLEAR-{int(timestamp)}',
                            event_type='alarm_cleared',
                            timestamp=timestamp,
                            severity='info',
                            summary=f'{definition.summary} cleared',
                            source_kind=definition.source_kind,
                            source_id=definition.source_id,
                            alarm_id=definition.alarm_id,
                            attributes=self._event_attributes(definition=definition, snapshot=snapshot, lifecycle=lifecycle, acknowledged=acknowledged),
                        )
                    )
                )
        return EventEvaluationResult(events=tuple(events), changed_alarm_ids=tuple(changed_alarm_ids))

    def acknowledge_with_event(
        self,
        *,
        alarm_id: AlarmId,
        actor: ActorId,
        timestamp: EventTime,
        authorization_decision: AuthorizationDecision | None = None,
        event_id: str | None = None,
        correlation_id: str | None = None,
    ) -> tuple[AlarmLifecycle, EventRecord | None]:
        before = self.active_statuses.get(alarm_id)
        lifecycle = self.acknowledge(
            alarm_id=alarm_id,
            actor=actor,
            timestamp=timestamp,
            authorization_decision=authorization_decision,
        )
        if authorization_decision is not None and not authorization_decision.allowed:
            return lifecycle, None
        if before is None:
            return lifecycle, None
        event = self._append_event(
            event=EventRecord(
                event_id=f'EVT-{alarm_id}-ACK-{int(timestamp)}' if event_id is None else event_id,
                event_type='alarm_acknowledged',
                timestamp=timestamp,
                severity='info',
                summary=f'{before.summary} acknowledged',
                source_kind=before.source_kind,
                source_id=before.source_id,
                correlation_id=correlation_id,
                alarm_id=alarm_id,
                attributes={'actor': str(actor), 'acknowledged': True},
            )
        )
        return lifecycle, event

    def active_alarm_rows(self) -> tuple[dict[str, object], ...]:
        rows = [status.as_dict() for status in self.active_statuses.values() if status.active]
        rows.sort(key=lambda item: (item['severity'], item['alarm_id']))
        return tuple(rows)

    def recent_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows = [item.as_dict() for item in self.recent_events]
        return tuple(rows[-max(1, limit):])

    def recent_event_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        return self.recent_rows(limit=limit)

    def summary(self) -> dict[str, object]:
        active = [status for status in self.active_statuses.values() if status.active]
        severities = [status.severity for status in active]
        return {
            'definition_count': len(self.definitions),
            'active_alarm_count': len(active),
            'unacknowledged_alarm_count': sum(1 for status in active if not status.acknowledged),
            'highest_active_severity': self._highest_severity(severities),
            'recent_domain_event_count': len(self.recent_events),
        }

    def export_lifecycles(self) -> tuple[AlarmLifecycle, ...]:
        ordered = sorted(self.lifecycles.items(), key=lambda item: str(item[0]))
        return tuple(lifecycle for _, lifecycle in ordered)

    def _append_event(self, *, event: EventRecord) -> EventRecord:
        self.recent_events.append(event)
        return event

    @staticmethod
    def _highest_severity(severities: list[str]) -> str | None:
        if not severities:
            return None
        ranking = {'critical': 3, 'warning': 2, 'info': 1}
        ordered = sorted(severities, key=lambda item: ranking.get(item, 0), reverse=True)
        return ordered[0]

    @staticmethod
    def _event_attributes(
        *,
        definition: AlarmDefinition,
        snapshot: VariableSnapshot | None,
        lifecycle: AlarmLifecycle,
        acknowledged: bool,
    ) -> dict[str, object]:
        state = None if snapshot is None else snapshot.state.value
        quality = None if snapshot is None else snapshot.quality.value
        value = None if snapshot is None else snapshot.value
        return {
            'condition_kind': definition.condition_kind,
            'comparison': definition.comparison,
            'threshold': definition.threshold,
            'trigger_states': [item.value for item in definition.trigger_states],
            'trigger_qualities': [item.value for item in definition.trigger_qualities],
            'value': value,
            'state': state,
            'quality': quality,
            'acknowledged': acknowledged,
            'transition_count': len(lifecycle.transitions),
        }

    @staticmethod
    def _condition_is_active(*, definition: AlarmDefinition, snapshot: VariableSnapshot | None) -> bool:
        if snapshot is None:
            return False
        if definition.condition_kind == 'variable_state':
            return snapshot.state in definition.trigger_states or snapshot.quality in definition.trigger_qualities
        if definition.condition_kind == 'variable_threshold':
            try:
                value = float(snapshot.value)
            except (TypeError, ValueError):
                return False
            threshold = 0.0 if definition.threshold is None else float(definition.threshold)
            comparison = definition.comparison or '>'
            if comparison == '>':
                return value > threshold
            if comparison == '>=':
                return value >= threshold
            if comparison == '<':
                return value < threshold
            if comparison == '<=':
                return value <= threshold
            if comparison == '==':
                return value == threshold
            return False
        if definition.condition_kind == 'variable_boolean_true':
            return str(snapshot.value).lower() == 'true'
        return False
