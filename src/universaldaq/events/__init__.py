"""Bounded event and alarm models and services for the current platform spine."""

from .models import (
    AlarmDefinition,
    AlarmLifecycle,
    AlarmStatus,
    AlarmTransition,
    EventEvaluationResult,
    EventRecord,
)
from .services import AlarmLifecycleService

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-EVENTS',
    'implements_requirements': [
        'UDQ-REQ-EVT-001',
        'UDQ-REQ-EVT-002',
        'UDQ-REQ-ARCH-001',
        'UDQ-REQ-SEC-002',
    ],
    'governed_by': [
        'UDQ-EVT-SPEC-001',
        'UDQ-SEC-SPEC-001',
        'UDQ-IMP-MAP-001',
        'UDQ-IMP-GUIDE-001',
    ],
    'subsystem': 'Events',
    'invariant_hooks': [
        'UDQ-INV-TRANS-003',
        'UDQ-INV-EVID-002',
    ],
    'proof_scope': 'transition-based events and alarms derived from canonical runtime truth with attributable acknowledgment evidence and bounded coordination services',
}

__all__ = [
    'AlarmDefinition',
    'AlarmLifecycle',
    'AlarmLifecycleService',
    'AlarmStatus',
    'AlarmTransition',
    'EventEvaluationResult',
    'EventRecord',
    'MODULE_DECLARATION',
]
