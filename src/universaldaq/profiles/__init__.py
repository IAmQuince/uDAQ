"""Profile, continuity, and workspace restore models for the bounded save-point baseline."""

from .models import (
    BenchPersistenceState,
    OperatorNote,
    PersistedSessionSummary,
    ProfileSnapshot,
    RestorePlan,
    RestorePlanner,
    RestoreResult,
    WorkspaceState,
)
from .serializers import (
    BENCH_PERSISTENCE_SCHEMA_VERSION,
    deserialize_bench_persistence_state,
    deserialize_operator_note,
    deserialize_persisted_session_summary,
    deserialize_profile_snapshot,
    deserialize_workspace_state,
    serialize_bench_persistence_state,
    serialize_operator_note,
    serialize_persisted_session_summary,
    serialize_profile_snapshot,
    serialize_workspace_state,
)
from .store import FileBenchStateStore, FileProfileStore, InMemoryBenchStateStore, InMemoryProfileStore

MODULE_DECLARATION = {
    "module_id": "UDQ-CODE-PKG-PROFILES",
    "implements_requirements": [
        "UDQ-REQ-PROF-001",
        "UDQ-REQ-PROF-002",
        "UDQ-REQ-ARCH-002",
    ],
    "governed_by": [
        "UDQ-PROF-SPEC-001",
        "UDQ-IMP-MAP-001",
        "UDQ-IMP-GUIDE-001",
    ],
    "subsystem": "Profiles",
    "invariant_hooks": [
        "UDQ-INV-STATE-002",
        "UDQ-INV-TRANS-002",
        "UDQ-INV-EVID-003",
    ],
    "proof_scope": "restore-origin workspace rebuilds, bounded profile persistence, operator-note continuity, and safe bench-state restore without physical apply publication",
}

__all__ = [
    "BENCH_PERSISTENCE_SCHEMA_VERSION",
    "BenchPersistenceState",
    "FileBenchStateStore",
    "FileProfileStore",
    "InMemoryBenchStateStore",
    "InMemoryProfileStore",
    "MODULE_DECLARATION",
    "OperatorNote",
    "PersistedSessionSummary",
    "ProfileSnapshot",
    "RestorePlan",
    "RestorePlanner",
    "RestoreResult",
    "WorkspaceState",
    "deserialize_bench_persistence_state",
    "deserialize_operator_note",
    "deserialize_persisted_session_summary",
    "deserialize_profile_snapshot",
    "deserialize_workspace_state",
    "serialize_bench_persistence_state",
    "serialize_operator_note",
    "serialize_persisted_session_summary",
    "serialize_profile_snapshot",
    "serialize_workspace_state",
]
