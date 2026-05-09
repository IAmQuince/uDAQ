"""Signal identity, dependency, and derived-evaluation models for the bounded save-point baseline."""

from .bindings import (
    BindingPolicy,
    BindingResolutionStatus,
    BindingReviewItem,
    BindingReviewSummary,
    DevicePointDefinition,
    LogicalOutputBinding,
    LogicalSignalBinding,
    SignalBindingService,
)
from .dependency_graph import dependency_graph, find_cycles, validate_derived_signals
from .models import DerivedSignalDefinition, SignalDefinition
from .registry import DerivedEvaluationResult, SignalRegistry, SignalSnapshot
from .validators import validate_for_activation
from .variables import (
    VariableDefinition,
    VariableEvaluationResult,
    VariableEvaluationService,
    VariableSnapshot,
    VariableSourceKind,
    VariableState,
)

MODULE_DECLARATION = {
    "module_id": "UDQ-CODE-PKG-SIGNALS",
    "implements_requirements": [
        "UDQ-REQ-SIG-001",
        "UDQ-REQ-SIG-002",
        "UDQ-REQ-ARCH-001",
    ],
    "governed_by": [
        "UDQ-SIG-SPEC-001",
        "UDQ-IMP-MAP-001",
        "UDQ-IMP-GUIDE-001",
    ],
    "subsystem": "Signals",
    "invariant_hooks": [
        "UDQ-INV-STATE-005",
        "UDQ-INV-TRANS-005",
    ],
    "proof_scope": "signal identity preservation, point-to-signal/output binding, variable evaluation, derived-signal validation, and bounded registry publication",
}

__all__ = [
    "BindingPolicy",
    "BindingResolutionStatus",
    "BindingReviewItem",
    "BindingReviewSummary",
    "DerivedEvaluationResult",
    "DevicePointDefinition",
    "LogicalOutputBinding",
    "LogicalSignalBinding",
    "DerivedSignalDefinition",
    "MODULE_DECLARATION",
    "SignalDefinition",
    "SignalBindingService",
    "SignalRegistry",
    "SignalSnapshot",
    "dependency_graph",
    "VariableDefinition",
    "VariableEvaluationResult",
    "VariableEvaluationService",
    "VariableSnapshot",
    "VariableSourceKind",
    "VariableState",
    "find_cycles",
    "validate_derived_signals",
    "validate_for_activation",
]
