from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from universaldaq.common import EventTime

from .models import GovernedActionClaimRow, GovernedActionClaimStatus


@dataclass(slots=True)
class GovernedActionClaimService:
    active_claims: dict[str, GovernedActionClaimRow] = field(default_factory=dict)
    recent_rows_buffer: deque[GovernedActionClaimRow] = field(default_factory=lambda: deque(maxlen=64))

    def has_active_claim(self, *, claim_key: str) -> bool:
        return claim_key in self.active_claims

    def claim(
        self,
        *,
        claim_key: str,
        governed_action: str,
        target_kind: str,
        target_id: str,
        claimed_by: str,
        correlation_id: str | None,
        timestamp: EventTime,
    ) -> GovernedActionClaimRow:
        row = GovernedActionClaimRow(
            claim_key=claim_key,
            governed_action=governed_action,
            target_kind=target_kind,
            target_id=target_id,
            claimed_by=claimed_by,
            timestamp=timestamp,
            status=GovernedActionClaimStatus.CLAIMED,
            correlation_id=correlation_id,
        )
        self.active_claims[claim_key] = row
        self.recent_rows_buffer.append(row)
        return row

    def resolve(
        self,
        *,
        claim_key: str,
        timestamp: EventTime,
        status: GovernedActionClaimStatus,
        command_id: str | None,
        reason: str | None,
    ) -> GovernedActionClaimRow | None:
        claim = self.active_claims.pop(claim_key, None)
        if claim is None:
            return None
        row = GovernedActionClaimRow(
            claim_key=claim.claim_key,
            governed_action=claim.governed_action,
            target_kind=claim.target_kind,
            target_id=claim.target_id,
            claimed_by=claim.claimed_by,
            timestamp=timestamp,
            status=status,
            correlation_id=claim.correlation_id,
            command_id=command_id,
            reason=reason,
        )
        self.recent_rows_buffer.append(row)
        return row

    def record_suppression(
        self,
        *,
        claim_key: str,
        governed_action: str,
        target_kind: str,
        target_id: str,
        claimed_by: str,
        correlation_id: str | None,
        timestamp: EventTime,
        reason: str,
    ) -> GovernedActionClaimRow:
        row = GovernedActionClaimRow(
            claim_key=claim_key,
            governed_action=governed_action,
            target_kind=target_kind,
            target_id=target_id,
            claimed_by=claimed_by,
            timestamp=timestamp,
            status=GovernedActionClaimStatus.SUPPRESSED,
            correlation_id=correlation_id,
            reason=reason,
        )
        self.recent_rows_buffer.append(row)
        return row

    def summary(self) -> dict[str, object]:
        rows = list(self.recent_rows_buffer)
        return {
            'active_claim_count': len(self.active_claims),
            'recent_claim_row_count': len(rows),
            'suppressed_count': sum(1 for item in rows if item.status == GovernedActionClaimStatus.SUPPRESSED),
            'completed_count': sum(1 for item in rows if item.status == GovernedActionClaimStatus.COMPLETED),
            'rejected_count': sum(1 for item in rows if item.status == GovernedActionClaimStatus.REJECTED),
        }

    def recent_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows = [row.as_dict() for row in self.recent_rows_buffer]
        return tuple(rows[-max(1, limit):])
