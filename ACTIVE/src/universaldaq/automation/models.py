from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from universaldaq.common import EventTime


class GovernedActionClaimStatus(StrEnum):
    CLAIMED = 'claimed'
    COMPLETED = 'completed'
    REJECTED = 'rejected'
    SUPPRESSED = 'suppressed'


@dataclass(frozen=True, slots=True, kw_only=True)
class GovernedActionClaimRow:
    claim_key: str
    governed_action: str
    target_kind: str
    target_id: str
    claimed_by: str
    timestamp: EventTime
    status: GovernedActionClaimStatus
    correlation_id: str | None = None
    command_id: str | None = None
    reason: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            'claim_key': self.claim_key,
            'governed_action': self.governed_action,
            'target_kind': self.target_kind,
            'target_id': self.target_id,
            'claimed_by': self.claimed_by,
            'timestamp': int(self.timestamp),
            'status': self.status.value,
            'correlation_id': self.correlation_id,
            'command_id': self.command_id,
            'reason': self.reason,
        }
