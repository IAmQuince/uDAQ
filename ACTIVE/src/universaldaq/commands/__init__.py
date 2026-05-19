"""Bounded command admission models and services for the shell control-entry spine."""

from .models import (
    CommandAdmissionStatus,
    CommandDispatchStatus,
    CommandIntent,
    CommandRecord,
    CommandRecordFactory,
    CommandRejectionCode,
)
from .services import CommandAdmissionService

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-COMMANDS',
    'implements_requirements': [
        'UDQ-REQ-OUT-001',
        'UDQ-REQ-OUT-002',
        'UDQ-REQ-EVT-002',
    ],
    'governed_by': [
        'UDQ-OUT-SPEC-001',
        'UDQ-EVT-SPEC-001',
    ],
    'subsystem': 'Commands',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-EVID-004',
    ],
    'proof_scope': 'bounded command admission records, dry-run and rejected command proof paths, and official alarm acknowledgment command entry into the canonical journal path',
}

__all__ = [
    'CommandAdmissionService',
    'CommandAdmissionStatus',
    'CommandDispatchStatus',
    'CommandIntent',
    'CommandRecord',
    'CommandRecordFactory',
    'CommandRejectionCode',
    'MODULE_DECLARATION',
]
