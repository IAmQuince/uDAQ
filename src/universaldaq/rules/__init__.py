"""Bounded rule models and services for the orchestration skeleton."""

from .models import AutomationActionRequest, RuleDefinition, RuleEvaluationResult, RuleOutcome, RuleRow
from .services import RuleEvaluationService

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-RULES',
    'implements_requirements': [
        'UDQ-REQ-LOG-001',
        'UDQ-REQ-EVT-002',
        'UDQ-REQ-OUT-002',
    ],
    'governed_by': [
        'UDQ-LOG-SPEC-001',
        'UDQ-SEQ-SPEC-001',
        'UDQ-OUT-SPEC-001',
    ],
    'subsystem': 'Rules',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-EVID-004',
    ],
    'proof_scope': 'bounded rule evaluation that observes canonical runtime truth and emits governed command intent through the official command-admission path',
}

__all__ = [
    'AutomationActionRequest',
    'MODULE_DECLARATION',
    'RuleDefinition',
    'RuleEvaluationResult',
    'RuleEvaluationService',
    'RuleOutcome',
    'RuleRow',
]
