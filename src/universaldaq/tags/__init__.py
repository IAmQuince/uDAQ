"""Canonical cross-device tag definitions and read-side acquisition broker services."""

from .models import (
    CanonicalTagDefinition,
    CanonicalTagProjection,
    CanonicalTagSample,
    MultiAdapterPollBatch,
    TagDirection,
    TagTimestampSource,
    TagValueType,
)
from .services import CanonicalTagRegistryService, MultiAdapterAcquisitionBroker

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-TAGS',
    'implements_requirements': [
        'UDQ-REQ-ARCH-001',
        'UDQ-REQ-SIG-001',
        'UDQ-REQ-DEV-001',
    ],
    'governed_by': [
        'UDQ-IMP-GUIDE-001',
        'UDQ-DEV-SPEC-001',
    ],
    'subsystem': 'Canonical Tags',
    'invariant_hooks': [
        'UDQ-INV-STATE-004',
        'UDQ-INV-TIME-001',
    ],
    'proof_scope': 'cross-device canonical tag definitions, normalized tag samples, and bounded multi-adapter read-side acquisition broker behavior without vendor-specific imports in the universal core',
}

__all__ = [
    'CanonicalTagDefinition',
    'CanonicalTagProjection',
    'CanonicalTagRegistryService',
    'CanonicalTagSample',
    'MODULE_DECLARATION',
    'MultiAdapterAcquisitionBroker',
    'MultiAdapterPollBatch',
    'TagDirection',
    'TagTimestampSource',
    'TagValueType',
]
