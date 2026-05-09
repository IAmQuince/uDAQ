"""Application-shell bootstrap, orchestration, and service composition for the bounded authorization-aware shell baseline."""

from .bootstrap import BootstrappedShell, ShellBootstrapper
from .authoritative_binding_bridge import (
    AuthoritativeBindingInventory,
    AuthoritativeBindingRow,
    BackendBindingReadbackProvider,
    BindingReadbackStatus,
    build_authoritative_binding_inventory,
)
from .first_signal import FirstSignalBindingDecision, FirstSignalPlanner, FirstSignalReplayTape
from .controller import AUTOSAVE_PROFILE_ID, LAST_SESSION_PROFILE_ID, ShellActionResult, ShellController
from .mapping_apply_preflight import (
    DraftBindingRow,
    MappingApplyMode,
    MappingApplyRequest,
    MappingChangeKind,
    MappingChangeProposal,
    MappingChangeSet,
    MappingPreflightIssue,
    MappingPreflightResult,
    MappingPreflightSeverity,
    MappingPreflightState,
    MappingPreflightValidator,
    MappingReviewLine,
    MappingReviewSummary,
    build_mapping_change_set,
    build_mapping_review_summary,
    draft_binding_from_mapping_row,
    prepare_mapping_apply_request,
)
from .lifecycle_orchestrator import ShellLifecycleOrchestrator
from .models import SprintOneModelSlice
from .service_registry import ShellServiceRegistry, build_default_service_registry
from .session import ShellSession
from .session_review import LightweightSessionReport, SessionReviewBuilder, SessionReviewDetail, SessionReviewListItem

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-APP',
    'implements_requirements': [
        'UDQ-REQ-ARCH-001',
        'UDQ-REQ-ARCH-002',
        'UDQ-REQ-UI-006',
        'UDQ-REQ-SEC-001',
    ],
    'governed_by': [
        'UDQ-IMP-MAP-001',
        'UDQ-ARCH-NAR-002',
        'UDQ-UI-NAR-001',
        'UDQ-SEC-SPEC-001',
        'UDQ-IMP-GUIDE-001',
    ],
    'subsystem': 'ApplicationShell',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-STATE-002',
        'UDQ-INV-EVID-004',
    ],
    'proof_scope': 'typed shell-level composition, backend-governed authorization decisions, bootstrap, orchestration, and bounded service registry for shell workflows',
}

__all__ = [
    'AUTOSAVE_PROFILE_ID',
    'AuthoritativeBindingInventory',
    'AuthoritativeBindingRow',
    'BackendBindingReadbackProvider',
    'BindingReadbackStatus',
    'BootstrappedShell',
    'FirstSignalBindingDecision',
    'FirstSignalPlanner',
    'FirstSignalReplayTape',
    'LAST_SESSION_PROFILE_ID',
    'prepare_mapping_apply_request',
    'draft_binding_from_mapping_row',
    'build_mapping_review_summary',
    'build_mapping_change_set',
    'MappingReviewSummary',
    'MappingReviewLine',
    'MappingPreflightValidator',
    'MappingPreflightState',
    'MappingPreflightSeverity',
    'MappingPreflightResult',
    'MappingPreflightIssue',
    'MappingChangeSet',
    'MappingChangeProposal',
    'MappingChangeKind',
    'MappingApplyRequest',
    'MappingApplyMode',
    'DraftBindingRow',
    'MODULE_DECLARATION',
    'ShellActionResult',
    'ShellBootstrapper',
    'ShellController',
    'ShellLifecycleOrchestrator',
    'ShellServiceRegistry',
    'ShellSession',
    'SessionReviewBuilder',
    'SessionReviewDetail',
    'SessionReviewListItem',
    'LightweightSessionReport',
    'SprintOneModelSlice',
    'build_authoritative_binding_inventory',
    'build_default_service_registry',
]
