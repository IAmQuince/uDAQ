from __future__ import annotations

import json
import re
from pathlib import Path

from .models import SessionCheckpoint
from .services import write_json

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class SessionCheckpointStoreError(ValueError):
    """Raised when a checkpoint store operation cannot complete safely."""


class CheckpointNotFoundError(SessionCheckpointStoreError):
    """Raised when a requested checkpoint is absent from the store."""


def _require_safe_id(value: str, *, field_name: str) -> str:
    if not _SAFE_ID.fullmatch(value):
        raise SessionCheckpointStoreError(f"{field_name} is not path-safe: {value!r}")
    return value


class FileSystemSessionCheckpointStore:
    """Filesystem-backed checkpoint store for local review-only session evidence."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def checkpoint_path(self, *, session_id: str, checkpoint_id: str) -> Path:
        safe_session = _require_safe_id(session_id, field_name="session_id")
        safe_checkpoint = _require_safe_id(checkpoint_id, field_name="checkpoint_id")
        return self.root / safe_session / f"{safe_checkpoint}.json"

    def save_checkpoint(self, checkpoint: SessionCheckpoint) -> Path:
        path = self.checkpoint_path(
            session_id=checkpoint.session_id,
            checkpoint_id=checkpoint.checkpoint_id,
        )
        return write_json(path, checkpoint.to_dict())

    def load_checkpoint(self, *, session_id: str, checkpoint_id: str) -> SessionCheckpoint:
        path = self.checkpoint_path(session_id=session_id, checkpoint_id=checkpoint_id)
        if not path.exists():
            raise CheckpointNotFoundError(f"checkpoint not found: {session_id}/{checkpoint_id}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise TypeError("checkpoint payload must be a JSON object")
            checkpoint = SessionCheckpoint.from_dict(payload)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise SessionCheckpointStoreError(f"invalid checkpoint payload: {path}") from exc
        if checkpoint.checkpoint_hash != payload.get("checkpoint_hash"):
            raise SessionCheckpointStoreError(f"checkpoint hash mismatch: {path}")
        return checkpoint

    def list_checkpoints(self, *, session_id: str) -> tuple[SessionCheckpoint, ...]:
        safe_session = _require_safe_id(session_id, field_name="session_id")
        session_root = self.root / safe_session
        if not session_root.exists():
            return ()
        checkpoints = [
            self.load_checkpoint(session_id=safe_session, checkpoint_id=path.stem)
            for path in sorted(session_root.glob("*.json"))
        ]
        return tuple(checkpoints)
