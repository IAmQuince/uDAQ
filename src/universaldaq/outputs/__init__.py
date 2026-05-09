"""Output request, apply, observe, and mismatch models for the bounded save-point baseline."""

from .arbiter import ArbitrationOutcome, OutputArbiter
from .broker import CommandArbitrationBroker
from .models import (
    BrokerEvent,
    CommandExecutionResult,
    CommandTrace,
    CommandTraceFactory,
    OutputAppliedState,
    OutputComparison,
    OutputObservedState,
    OutputRequest,
    OwnershipLease,
    SafeStatePolicy,
    WritableTagBinding,
)
from .services import OutputCommandService
from .validators import validate_command_trace

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-OUTPUTS',
    'implements_requirements': [
        'UDQ-REQ-OUT-001',
        'UDQ-REQ-OUT-002',
        'UDQ-REQ-ARCH-001',
        'UDQ-REQ-SEC-002',
    ],
    'governed_by': [
        'UDQ-OUT-SPEC-001',
        'UDQ-SEC-SPEC-001',
        'UDQ-IMP-MAP-001',
        'UDQ-IMP-GUIDE-001',
    ],
    'subsystem': 'Outputs',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-TRANS-001',
        'UDQ-INV-TIME-002',
    ],
    'proof_scope': 'requested/applied/observed traces, explicit authorization-denied outcomes, and bounded arbitration without physical writes',
}

__all__ = [
    'ArbitrationOutcome',
    'BrokerEvent',
    'CommandArbitrationBroker',
    'CommandExecutionResult',
    'CommandTrace',
    'CommandTraceFactory',
    'MODULE_DECLARATION',
    'OutputAppliedState',
    'OutputArbiter',
    'OutputCommandService',
    'OutputComparison',
    'OutputObservedState',
    'OutputRequest',
    'OwnershipLease',
    'SafeStatePolicy',
    'WritableTagBinding',
    'validate_command_trace',
]
