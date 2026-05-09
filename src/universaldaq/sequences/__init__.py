"""Bounded sequence models and services for the orchestration skeleton."""

from .models import SequenceDefinition, SequenceEvaluationResult, SequenceRow, SequenceStatus, SequenceStep
from .services import SequenceService

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-SEQUENCES',
    'implements_requirements': [
        'UDQ-REQ-SEQ-001',
        'UDQ-REQ-OUT-002',
        'UDQ-REQ-EVT-002',
    ],
    'governed_by': [
        'UDQ-SEQ-SPEC-001',
        'UDQ-OUT-SPEC-001',
    ],
    'subsystem': 'Sequences',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-EVID-004',
    ],
    'proof_scope': 'bounded sequence state transitions that wait on canonical alarm truth and emit governed command intent through the official command-admission path',
}

__all__ = [
    'MODULE_DECLARATION',
    'SequenceDefinition',
    'SequenceEvaluationResult',
    'SequenceRow',
    'SequenceService',
    'SequenceStatus',
    'SequenceStep',
]
