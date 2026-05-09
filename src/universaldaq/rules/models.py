from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

from universaldaq.common import EventTime


class RuleOutcome(StrEnum):
    NO_MATCH = 'no_match'
    TRIGGERED = 'triggered'
    SUPPRESSED = 'suppressed'
    DISABLED = 'disabled'


@dataclass(frozen=True, slots=True, kw_only=True)
class AutomationActionRequest:
    source_kind: str
    source_id: str
    action_kind: str
    action_payload: Mapping[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            'source_kind': self.source_kind,
            'source_id': self.source_id,
            'action_kind': self.action_kind,
            'action_payload': {str(key): value for key, value in self.action_payload.items()},
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleDefinition:
    rule_id: str
    condition_kind: str
    action_kind: str
    enabled: bool = True
    condition_payload: Mapping[str, object] = field(default_factory=dict)
    action_payload: Mapping[str, object] = field(default_factory=dict)
    cooldown_ticks: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            'rule_id': self.rule_id,
            'condition_kind': self.condition_kind,
            'action_kind': self.action_kind,
            'enabled': self.enabled,
            'condition_payload': {str(key): value for key, value in self.condition_payload.items()},
            'action_payload': {str(key): value for key, value in self.action_payload.items()},
            'cooldown_ticks': self.cooldown_ticks,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleRow:
    rule_id: str
    timestamp: EventTime
    outcome: RuleOutcome
    condition_active: bool
    action_kind: str | None = None
    command_id: str | None = None
    correlation_id: str | None = None
    claim_key: str | None = None
    suppression_reason: str | None = None
    result_summary: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            'rule_id': self.rule_id,
            'timestamp': int(self.timestamp),
            'outcome': self.outcome.value,
            'condition_active': self.condition_active,
            'action_kind': self.action_kind,
            'command_id': self.command_id,
            'correlation_id': self.correlation_id,
            'claim_key': self.claim_key,
            'suppression_reason': self.suppression_reason,
            'result_summary': self.result_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleEvaluationResult:
    action_requests: tuple[AutomationActionRequest, ...] = ()
    rows: tuple[RuleRow, ...] = ()
