from __future__ import annotations

import hashlib
import json

from .models import DurableSession, ReplayMode, ReplayView, SessionCheckpoint

REPLAY_EVIDENCE_SCHEMA_VERSION = "udq.session.replay.evidence.v1"


def _canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _evidence_hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_checkpoint_replay_evidence(
    *,
    replay: ReplayView,
    checkpoint: SessionCheckpoint | None = None,
    session: DurableSession | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": REPLAY_EVIDENCE_SCHEMA_VERSION,
        "session_id": replay.session_id,
        "checkpoint_id": replay.checkpoint_id,
        "replay_id": replay.replay_id,
        "replay_mode": replay.replay_mode.value,
        "authority_scope": replay.authority_scope,
        "replay_is_live": replay.replay_is_live,
        "runtime_snapshot_hash": replay.runtime_snapshot_hash,
        "checkpoint_hash": checkpoint.checkpoint_hash
        if checkpoint is not None
        else replay.checkpoint_hash,
        "validation": replay.validation.to_dict(),
        "safety": replay.safety.to_dict(),
        "summary": replay.summary,
        "known_limitations": list(checkpoint.known_limitations if checkpoint is not None else ()),
        "session_checkpoint_count": len(session.checkpoints) if session is not None else None,
    }
    payload["replay_evidence_hash"] = _evidence_hash(payload)
    return payload


__all__ = [
    "REPLAY_EVIDENCE_SCHEMA_VERSION",
    "ReplayMode",
    "ReplayView",
    "build_checkpoint_replay_evidence",
]
