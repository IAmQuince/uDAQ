from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.commands import CommandRecord
from universaldaq.common import EventTime
from universaldaq.events import AlarmStatus
from universaldaq.rules.models import AutomationActionRequest

from .models import SequenceDefinition, SequenceEvaluationResult, SequenceRow, SequenceStatus


@dataclass(slots=True)
class _SequenceState:
    status: SequenceStatus = SequenceStatus.IDLE
    current_step_index: int = 0
    started_at: EventTime | None = None
    last_changed_at: EventTime | None = None
    last_result: str | None = None
    awaiting_command: bool = False


@dataclass(slots=True)
class SequenceService:
    definitions: dict[str, SequenceDefinition] = field(default_factory=dict)
    states: dict[str, _SequenceState] = field(default_factory=dict)
    recent_rows_buffer: deque[SequenceRow] = field(default_factory=lambda: deque(maxlen=64))

    def register(self, definition: SequenceDefinition) -> None:
        self.definitions[definition.sequence_id] = definition
        self.states.setdefault(definition.sequence_id, _SequenceState())

    def start(self, *, sequence_id: str, timestamp: EventTime) -> tuple[SequenceRow, ...]:
        definition = self.definitions.get(sequence_id)
        if definition is None:
            return ()
        state = self.states.setdefault(sequence_id, _SequenceState())
        state.status = SequenceStatus.RUNNING if definition.enabled else SequenceStatus.STOPPED
        state.current_step_index = 0
        state.started_at = timestamp
        state.last_changed_at = timestamp
        state.last_result = 'started' if definition.enabled else 'disabled'
        state.awaiting_command = False
        row = SequenceRow(
            sequence_id=sequence_id,
            timestamp=timestamp,
            status=state.status,
            current_step_index=state.current_step_index,
            event='started' if definition.enabled else 'disabled',
        )
        self.recent_rows_buffer.append(row)
        return (row,)

    def evaluate(
        self,
        *,
        timestamp: EventTime,
        active_alarm_statuses: Mapping[object, AlarmStatus],
    ) -> SequenceEvaluationResult:
        actions: list[AutomationActionRequest] = []
        rows: list[SequenceRow] = []
        active_alarm_map = {str(key): value for key, value in active_alarm_statuses.items()}
        for sequence_id, definition in self.definitions.items():
            state = self.states.setdefault(sequence_id, _SequenceState())
            if state.status != SequenceStatus.RUNNING or state.awaiting_command or not definition.enabled:
                continue
            while state.status == SequenceStatus.RUNNING and state.current_step_index < len(definition.steps):
                step = definition.steps[state.current_step_index]
                if step.step_kind == 'wait_alarm_active_unacknowledged':
                    alarm_id = str(step.payload.get('alarm_id', ''))
                    alarm = active_alarm_map.get(alarm_id)
                    if alarm is not None and alarm.active and not alarm.acknowledged:
                        row = self._advance(sequence_id=sequence_id, timestamp=timestamp, event='step_satisfied')
                        rows.append(row)
                        continue
                    break
                if step.step_kind == 'wait_alarm_active':
                    alarm_id = str(step.payload.get('alarm_id', ''))
                    alarm = active_alarm_map.get(alarm_id)
                    if alarm is not None and alarm.active:
                        row = self._advance(sequence_id=sequence_id, timestamp=timestamp, event='step_satisfied')
                        rows.append(row)
                        continue
                    break
                if step.step_kind == 'wait_alarm_inactive':
                    alarm_id = str(step.payload.get('alarm_id', ''))
                    alarm = active_alarm_map.get(alarm_id)
                    if alarm is None or not alarm.active:
                        row = self._advance(sequence_id=sequence_id, timestamp=timestamp, event='step_satisfied')
                        rows.append(row)
                        continue
                    break
                if step.step_kind in {'emit_ack_alarm', 'emit_dry_run_adapter_command'}:
                    action_kind = 'ack_alarm' if step.step_kind == 'emit_ack_alarm' else 'dry_run_adapter_command'
                    action = AutomationActionRequest(
                        source_kind='sequence',
                        source_id=sequence_id,
                        action_kind=action_kind,
                        action_payload=step.payload,
                    )
                    actions.append(action)
                    state.awaiting_command = True
                    state.last_changed_at = timestamp
                    state.last_result = f'action_emitted:{action_kind}'
                    row = SequenceRow(
                        sequence_id=sequence_id,
                        timestamp=timestamp,
                        status=state.status,
                        current_step_index=state.current_step_index,
                        event='action_emitted',
                    correlation_id=str(step.payload.get('correlation_id')) if step.payload.get('correlation_id') is not None else None,
                    )
                    self.recent_rows_buffer.append(row)
                    rows.append(row)
                    break
                state.status = SequenceStatus.FAILED
                state.last_changed_at = timestamp
                state.last_result = f'unsupported_step:{step.step_kind}'
                row = SequenceRow(
                    sequence_id=sequence_id,
                    timestamp=timestamp,
                    status=state.status,
                    current_step_index=state.current_step_index,
                    event='unsupported_step',
                    result_summary=state.last_result,
                )
                self.recent_rows_buffer.append(row)
                rows.append(row)
                break
            if state.status == SequenceStatus.RUNNING and state.current_step_index >= len(definition.steps):
                state.status = SequenceStatus.COMPLETED
                state.last_changed_at = timestamp
                state.last_result = 'completed'
                row = SequenceRow(
                    sequence_id=sequence_id,
                    timestamp=timestamp,
                    status=state.status,
                    current_step_index=state.current_step_index,
                    event='completed',
                    result_summary='sequence completed',
                )
                self.recent_rows_buffer.append(row)
                rows.append(row)
        return SequenceEvaluationResult(action_requests=tuple(actions), rows=tuple(rows))

    def apply_command_result(self, *, sequence_id: str, record: CommandRecord, timestamp: EventTime) -> tuple[SequenceRow, ...]:
        state = self.states.setdefault(sequence_id, _SequenceState())
        if not state.awaiting_command:
            return ()
        state.awaiting_command = False
        rows: list[SequenceRow] = []
        if record.rejected:
            state.status = SequenceStatus.FAILED
            state.last_result = record.rejection_reason or record.result_summary
            row = SequenceRow(
                sequence_id=sequence_id,
                timestamp=timestamp,
                status=state.status,
                current_step_index=state.current_step_index,
                event='command_rejected',
                command_id=record.intent.command_id,
                correlation_id=record.intent.correlation_id,
                result_summary=state.last_result,
            )
            self.recent_rows_buffer.append(row)
            rows.append(row)
            state.last_changed_at = timestamp
            return tuple(rows)
        state.current_step_index += 1
        state.last_changed_at = timestamp
        state.last_result = record.result_summary
        advance = SequenceRow(
            sequence_id=sequence_id,
            timestamp=timestamp,
            status=state.status,
            current_step_index=state.current_step_index,
            event='command_admitted',
            command_id=record.intent.command_id,
            correlation_id=record.intent.correlation_id,
            result_summary=record.result_summary,
        )
        self.recent_rows_buffer.append(advance)
        rows.append(advance)
        definition = self.definitions.get(sequence_id)
        if definition is not None and state.current_step_index >= len(definition.steps):
            state.status = SequenceStatus.COMPLETED
            complete = SequenceRow(
                sequence_id=sequence_id,
                timestamp=timestamp,
                status=state.status,
                current_step_index=state.current_step_index,
                event='completed',
                command_id=record.intent.command_id,
                correlation_id=record.intent.correlation_id,
                result_summary='sequence completed',
            )
            self.recent_rows_buffer.append(complete)
            rows.append(complete)
        return tuple(rows)

    def summary(self) -> dict[str, object]:
        statuses = [state.status for state in self.states.values()]
        return {
            'sequence_count': len(self.definitions),
            'running_count': sum(1 for item in statuses if item == SequenceStatus.RUNNING),
            'completed_count': sum(1 for item in statuses if item == SequenceStatus.COMPLETED),
            'failed_count': sum(1 for item in statuses if item == SequenceStatus.FAILED),
            'recent_sequence_row_count': len(self.recent_rows_buffer),
        }

    def recent_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows = [row.as_dict() for row in self.recent_rows_buffer]
        return tuple(rows[-max(1, limit):])

    def record_action_suppressed(
        self,
        *,
        sequence_id: str,
        timestamp: EventTime,
        action_kind: str,
        claim_key: str | None,
        correlation_id: str | None,
        reason: str,
    ) -> SequenceRow:
        state = self.states.setdefault(sequence_id, _SequenceState())
        state.awaiting_command = False
        state.last_changed_at = timestamp
        state.last_result = reason
        row = SequenceRow(
            sequence_id=sequence_id,
            timestamp=timestamp,
            status=state.status,
            current_step_index=state.current_step_index,
            event='action_suppressed',
            correlation_id=correlation_id,
            claim_key=claim_key,
            suppression_reason=reason,
            result_summary=f'{action_kind}:{reason}',
        )
        self.recent_rows_buffer.append(row)
        return row

    def _advance(self, *, sequence_id: str, timestamp: EventTime, event: str) -> SequenceRow:
        state = self.states.setdefault(sequence_id, _SequenceState())
        state.current_step_index += 1
        state.last_changed_at = timestamp
        state.last_result = event
        row = SequenceRow(
            sequence_id=sequence_id,
            timestamp=timestamp,
            status=state.status,
            current_step_index=state.current_step_index,
            event=event,
        )
        self.recent_rows_buffer.append(row)
        return row
