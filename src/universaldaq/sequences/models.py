from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

from universaldaq.common import EventTime
from universaldaq.rules.models import AutomationActionRequest


class SequenceStatus(StrEnum):
    IDLE = 'idle'
    RUNNING = 'running'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'
    STOPPED = 'stopped'


@dataclass(frozen=True, slots=True, kw_only=True)
class SequenceStep:
    step_id: str
    step_kind: str
    payload: Mapping[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            'step_id': self.step_id,
            'step_kind': self.step_kind,
            'payload': {str(key): value for key, value in self.payload.items()},
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class SequenceDefinition:
    sequence_id: str
    steps: tuple[SequenceStep, ...]
    enabled: bool = True

    def as_dict(self) -> dict[str, object]:
        return {
            'sequence_id': self.sequence_id,
            'enabled': self.enabled,
            'steps': [step.as_dict() for step in self.steps],
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class SequenceRow:
    sequence_id: str
    timestamp: EventTime
    status: SequenceStatus
    current_step_index: int
    event: str
    command_id: str | None = None
    correlation_id: str | None = None
    claim_key: str | None = None
    suppression_reason: str | None = None
    result_summary: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            'sequence_id': self.sequence_id,
            'timestamp': int(self.timestamp),
            'status': self.status.value,
            'current_step_index': self.current_step_index,
            'event': self.event,
            'command_id': self.command_id,
            'correlation_id': self.correlation_id,
            'claim_key': self.claim_key,
            'suppression_reason': self.suppression_reason,
            'result_summary': self.result_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class SequenceEvaluationResult:
    action_requests: tuple[AutomationActionRequest, ...] = ()
    rows: tuple[SequenceRow, ...] = ()
