"""Typed common model exports for the bounded save-point baseline."""

from .enums import (
    AlarmLifecycleState,
    AuthorizationState,
    CommandDecision,
    EvidenceKind,
    ExportArtifactClass,
    GraphMode,
    RestoreOrigin,
    SignalQuality,
)
from .evidence import EvidenceRecord
from .ids import AlarmId, ActorId, EvidenceId, OutputId, ProfileId, RequestId, SignalId, TraceId, VariableId
from .metrics import NullMetrics, RuntimeMetricsStore, TimingStat
from .result import ValidationFinding, ValidationReport
from .timebase import EventTime, as_event_time

MODULE_DECLARATION = {
    "module_id": "UDQ-CODE-PKG-COMMON",
    "implements_requirements": [
        "UDQ-REQ-ARCH-001",
        "UDQ-REQ-OUT-001",
        "UDQ-REQ-UI-006",
        "UDQ-REQ-EXP-001",
    ],
    "governed_by": [
        "UDQ-IMP-MAP-001",
        "UDQ-OUT-SPEC-001",
        "UDQ-IMP-GUIDE-001",
        "UDQ-EXP-SPEC-001",
    ],
    "subsystem": "SharedModels",
    "invariant_hooks": [
        "UDQ-INV-STATE-001",
        "UDQ-INV-STATE-004",
    ],
    "proof_scope": "shared shared bounded-baseline types, enums, evidence records, export classes, and validation models",
}

__all__ = [
    "AlarmId",
    "ActorId",
    "AlarmLifecycleState",
    "AuthorizationState",
    "CommandDecision",
    "EvidenceId",
    "EvidenceKind",
    "EvidenceRecord",
    "EventTime",
    "ExportArtifactClass",
    "GraphMode",
    "MODULE_DECLARATION",
    "OutputId",
    "ProfileId",
    "RequestId",
    "RestoreOrigin",
    "SignalId",
    "SignalQuality",
    "TraceId",
    "NullMetrics",
    "RuntimeMetricsStore",
    "TimingStat",
    "VariableId",
    "ValidationFinding",
    "ValidationReport",
    "as_event_time",
]
