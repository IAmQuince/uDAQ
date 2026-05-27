"""Durable session, checkpoint, and review-only replay spine."""

from .models import (
    DEFAULT_SOURCE_PACKAGE_ID,
    SESSION_AUTHORITY_SCOPE,
    SESSION_CHECKPOINT_SCHEMA_VERSION,
    SESSION_MODEL_VERSION,
    SESSION_REPLAY_SCHEMA_VERSION,
    DurableSession,
    ReplayMode,
    ReplayView,
    SessionCheckpoint,
    SessionMode,
    SessionSafetyPosture,
    SessionValidationResult,
)
from .replay import REPLAY_EVIDENCE_SCHEMA_VERSION, build_checkpoint_replay_evidence
from .restore import SessionRestoreResult, restore_review_session
from .services import (
    DurableSessionService,
    build_replay_evidence_from_checkpoint,
    build_replay_from_checkpoint,
    build_session_checkpoint,
    canonical_json,
    create_checkpoint_from_runtime_state,
    create_session,
    get_current_session_checkpoint,
    load_session,
    save_session,
    state_hash,
    validate_checkpoint_payload,
    validate_session_checkpoint,
    write_json,
)
from .store import (
    CheckpointNotFoundError,
    FileSystemSessionCheckpointStore,
    SessionCheckpointStoreError,
)

MODULE_DECLARATION = {
    "module_id": "UDQ-CODE-PKG-SESSION",
    "implements_requirements": [
        "UDQ-REQ-DIAG-001",
        "UDQ-REQ-HIS-001",
    ],
    "governed_by": [
        "UDQ-ROADMAP-SPEC-001",
    ],
    "subsystem": "SessionCheckpointReplay",
    "invariant_hooks": [
        "UDQ-INV-STATE-001",
        "UDQ-INV-STATE-004",
    ],
    "proof_scope": "durable review-only session checkpoints and non-live replay views over authoritative runtime snapshots",
}

__all__ = [
    "DEFAULT_SOURCE_PACKAGE_ID",
    "SESSION_AUTHORITY_SCOPE",
    "SESSION_CHECKPOINT_SCHEMA_VERSION",
    "SESSION_MODEL_VERSION",
    "SESSION_REPLAY_SCHEMA_VERSION",
    "CheckpointNotFoundError",
    "DurableSession",
    "DurableSessionService",
    "FileSystemSessionCheckpointStore",
    "MODULE_DECLARATION",
    "REPLAY_EVIDENCE_SCHEMA_VERSION",
    "ReplayMode",
    "ReplayView",
    "SessionCheckpoint",
    "SessionCheckpointStoreError",
    "SessionMode",
    "SessionRestoreResult",
    "SessionSafetyPosture",
    "SessionValidationResult",
    "build_checkpoint_replay_evidence",
    "build_replay_evidence_from_checkpoint",
    "build_replay_from_checkpoint",
    "build_session_checkpoint",
    "canonical_json",
    "create_checkpoint_from_runtime_state",
    "create_session",
    "get_current_session_checkpoint",
    "load_session",
    "restore_review_session",
    "save_session",
    "state_hash",
    "validate_checkpoint_payload",
    "validate_session_checkpoint",
    "write_json",
]
