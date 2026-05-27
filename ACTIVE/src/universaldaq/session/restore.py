from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .models import (
    SESSION_AUTHORITY_SCOPE,
    SessionCheckpoint,
    SessionSafetyPosture,
    SessionValidationResult,
)
from .services import DurableSessionService


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionRestoreResult:
    checkpoint_id: str
    session_id: str
    runtime_snapshot: Mapping[str, object]
    runtime_snapshot_hash: str
    checkpoint_hash: str
    validation: SessionValidationResult
    safety: SessionSafetyPosture
    authority_scope: str = SESSION_AUTHORITY_SCOPE
    summary: str = "checkpoint restored into review/session projection only"

    def to_dict(self) -> dict[str, object]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "session_id": self.session_id,
            "authority_scope": self.authority_scope,
            "runtime_snapshot_hash": self.runtime_snapshot_hash,
            "checkpoint_hash": self.checkpoint_hash,
            "runtime_snapshot": dict(self.runtime_snapshot),
            "validation": self.validation.to_dict(),
            "safety": self.safety.to_dict(),
            "summary": self.summary,
        }


def restore_review_session(checkpoint: SessionCheckpoint) -> SessionRestoreResult:
    validation = DurableSessionService().validate_checkpoint(checkpoint)
    if not validation.ok:
        raise ValueError(f"checkpoint is not safe to restore: {validation.errors}")
    return SessionRestoreResult(
        checkpoint_id=checkpoint.checkpoint_id,
        session_id=checkpoint.session_id,
        runtime_snapshot=checkpoint.runtime_snapshot,
        runtime_snapshot_hash=checkpoint.runtime_snapshot_hash,
        checkpoint_hash=checkpoint.checkpoint_hash,
        validation=validation,
        safety=checkpoint.safety,
    )
