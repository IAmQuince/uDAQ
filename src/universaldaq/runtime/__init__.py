"""Runtime quality services for bounded acquisition, presentation, and journaling."""

from .models import (
    AcquisitionBatch,
    BoundedRecordQueue,
    JournalEntry,
    JournalManifest,
    JournalSegmentInfo,
    JournalWriteResult,
    PersistedJournalEntry,
    PresentationSnapshot,
    QueuedItem,
    RuntimeStatus,
    SessionCheckpoint,
    SessionCheckpointWriteResult,
    VariableUpdateStats,
)
from .semantics import (
    RuntimeAudienceMetricLayers,
    RuntimeSemanticState,
    build_canonical_runtime_evidence_bundle,
    build_runtime_event_taxonomy,
    build_runtime_metric_layers,
    build_runtime_reviewer_rollup,
    build_runtime_semantic_state,
    build_runtime_truth_surface_inventory,
    build_runtime_vocabulary_map,
    reviewer_label_for_family,
    state_family_for,
)
from .services import AppendOnlyJournalService, RuntimeQualityService, SessionCheckpointService

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-RUNTIME',
    'implements_requirements': [
        'UDQ-REQ-DEV-001',
        'UDQ-REQ-DIAG-001',
    ],
    'governed_by': [
        'UDQ-PERF-SPEC-001',
    ],
    'subsystem': 'RuntimeQuality',
    'invariant_hooks': [
        'UDQ-INV-TIME-001',
    ],
    'proof_scope': 'bounded acquisition queueing, recent live buffering, presentation coalescing, append-only runtime journaling, and restart checkpoint scaffolding',
}

__all__ = [
    'AcquisitionBatch',
    'AppendOnlyJournalService',
    'RuntimeAudienceMetricLayers',
    'RuntimeSemanticState',
    'BoundedRecordQueue',
    'JournalEntry',
    'JournalManifest',
    'JournalSegmentInfo',
    'JournalWriteResult',
    'PersistedJournalEntry',
    'MODULE_DECLARATION',
    'PresentationSnapshot',
    'QueuedItem',
    'RuntimeQualityService',
    'build_canonical_runtime_evidence_bundle',
    'build_runtime_event_taxonomy',
    'build_runtime_metric_layers',
    'build_runtime_reviewer_rollup',
    'build_runtime_semantic_state',
    'build_runtime_truth_surface_inventory',
    'build_runtime_vocabulary_map',
    'RuntimeStatus',
    'SessionCheckpoint',
    'SessionCheckpointService',
    'SessionCheckpointWriteResult',
    'VariableUpdateStats',
    'reviewer_label_for_family',
    'state_family_for',
]
