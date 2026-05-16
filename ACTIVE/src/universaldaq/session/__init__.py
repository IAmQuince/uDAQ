"""Durable session, checkpoint, and review-only replay spine."""

from .models import (
    DEFAULT_SOURCE_PACKAGE_ID,
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
from .services import (
    DurableSessionService,
    build_replay_from_checkpoint,
    build_session_checkpoint,
    canonical_json,
    create_checkpoint_from_runtime_state,
    create_session,
    get_current_session_checkpoint,
    load_session,
    save_session,
    state_hash,
    validate_session_checkpoint,
    validate_checkpoint_payload,
    write_json,
)

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-SESSION',
    'implements_requirements': [
        'UDQ-REQ-DIAG-001',
        'UDQ-REQ-HIS-001',
    ],
    'governed_by': [
        'UDQ-ROADMAP-SPEC-001',
    ],
    'subsystem': 'SessionCheckpointReplay',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-STATE-004',
    ],
    'proof_scope': 'durable review-only session checkpoints and non-live replay views over authoritative runtime snapshots',
}

__all__ = [
    'DEFAULT_SOURCE_PACKAGE_ID',
    'SESSION_CHECKPOINT_SCHEMA_VERSION',
    'SESSION_MODEL_VERSION',
    'SESSION_REPLAY_SCHEMA_VERSION',
    'DurableSession',
    'DurableSessionService',
    'MODULE_DECLARATION',
    'ReplayMode',
    'ReplayView',
    'SessionCheckpoint',
    'SessionMode',
    'SessionSafetyPosture',
    'SessionValidationResult',
    'build_replay_from_checkpoint',
    'build_session_checkpoint',
    'canonical_json',
    'create_checkpoint_from_runtime_state',
    'create_session',
    'get_current_session_checkpoint',
    'load_session',
    'save_session',
    'state_hash',
    'validate_session_checkpoint',
    'validate_checkpoint_payload',
    'write_json',
]
