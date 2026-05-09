"""Bounded authorization models, policies, and services for governed shell actions."""

from .builtin_policies import (
    DEFAULT_ACTION_PERMISSIONS,
    DEFAULT_ROLE_ACTIONS,
    DEFAULT_ROLE_PERMISSIONS,
    derive_role_class_from_authority_state,
)
from .models import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationReasonCode,
    CapabilitySnapshot,
    GovernedAction,
    PermissionFamily,
    RoleClass,
)
from .policy import AuthorizationPolicy
from .services import AuthorizationService

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-SECURITY',
    'implements_requirements': [
        'UDQ-REQ-SEC-001',
        'UDQ-REQ-SEC-002',
        'UDQ-REQ-OUT-002',
        'UDQ-REQ-EVT-002',
        'UDQ-REQ-EXP-002',
    ],
    'governed_by': [
        'UDQ-SEC-SPEC-001',
        'UDQ-SEC-BASELINE-001',
        'UDQ-OUT-SPEC-001',
        'UDQ-EVT-SPEC-001',
        'UDQ-EXP-SPEC-001',
    ],
    'subsystem': 'Security',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-STATE-002',
        'UDQ-INV-EVID-004',
    ],
    'proof_scope': 'bounded authorization policy, typed governed actions, backend enforcement decisions, and attributable denial outcomes',
}

__all__ = [
    'ActorContext',
    'AuthorizationDecision',
    'AuthorizationPolicy',
    'AuthorizationReasonCode',
    'AuthorizationService',
    'CapabilitySnapshot',
    'DEFAULT_ACTION_PERMISSIONS',
    'DEFAULT_ROLE_ACTIONS',
    'DEFAULT_ROLE_PERMISSIONS',
    'GovernedAction',
    'MODULE_DECLARATION',
    'PermissionFamily',
    'RoleClass',
    'derive_role_class_from_authority_state',
]
