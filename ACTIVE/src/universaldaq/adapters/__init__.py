"""Adapter boundary contracts, discovery flows, support-pack seams, and simulated reference adapters."""

from .contracts import AdapterContract, DiscoveryProvider
from .discovery import AdapterInventoryDiscoveryProvider
from .errors import AdapterLifecycleError, DiscoveryProviderUnavailableError, UnknownDiscoveredDeviceError
from .reconciliation import (
    ConnectionInstance,
    ConnectionState,
    DeviceRecord,
    DeviceRegistryService,
    MatchConfidence,
    ReconciliationOutcome,
    ReconciliationOutcomeKind,
    RemapCandidate,
)
from .models import (
    AdapterCapability,
    AdapterCommandOutcome,
    AdapterCommandRequest,
    AdapterCommandResult,
    AdapterHealth,
    AdapterHealthState,
    AdapterKind,
    AdapterOperationMode,
    AdapterPointRef,
    AdapterPollResult,
    DeviceIdentity,
    DeviceLifecyclePhase,
    DeviceSupportTier,
    DiscoveredDevice,
    KnownDeviceRecord,
    PointClass,
    PointSnapshot,
    SupportPackDescriptor,
    SupportPackLoadReport,
    SupportPackLoadState,
    SupportPackProbeResult,
    SupportPackRegistration,
    WorkbenchDescriptor,
)
from .services import AdapterManagerService
from .support_pack_loader import discover_optional_support_pack_modules, load_optional_support_packs
from .capability_reports import (
    DiscoveredDeviceCapabilitySummary,
    RuntimeCapabilitySurvey,
    SupportPackCapabilitySummary,
    survey_runtime_capabilities,
)
from .fake_signal import DeterministicWaveformAdapter
from .simulated import SimulatedReadAdapter, SimulatedWritableAdapter

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-ADAPTERS',
    'implements_requirements': [
        'UDQ-REQ-DEV-001',
        'UDQ-REQ-DEV-002',
        'UDQ-REQ-MOD-002',
        'UDQ-REQ-DIAG-001',
    ],
    'governed_by': [
        'UDQ-DEV-SPEC-001',
        'UDQ-SEC-BASELINE-001',
        'UDQ-OUT-SPEC-001',
        'UDQ-IMP-GUIDE-001',
    ],
    'subsystem': 'Adapters',
    'invariant_hooks': [
        'UDQ-INV-STATE-001',
        'UDQ-INV-STATE-004',
        'UDQ-INV-TIME-001',
    ],
    'proof_scope': 'typed adapter boundary contracts, capability and health inventory, discovery and onboarding seams, support-pack registration, point snapshots, command handoff results, and simulated reference adapters without real hardware protocols',
}

__all__ = [
    'AdapterCapability',
    'AdapterCommandOutcome',
    'AdapterCommandRequest',
    'AdapterCommandResult',
    'AdapterContract',
    'AdapterHealth',
    'AdapterHealthState',
    'AdapterInventoryDiscoveryProvider',
    'AdapterLifecycleError',
    'ConnectionInstance',
    'ConnectionState',
    'DeviceRecord',
    'DeviceRegistryService',
    'MatchConfidence',
    'AdapterKind',
    'AdapterManagerService',
    'AdapterOperationMode',
    'AdapterPointRef',
    'AdapterPollResult',
    'DeviceIdentity',
    'DeviceLifecyclePhase',
    'DeterministicWaveformAdapter',
    'DeviceSupportTier',
    'DiscoveryProvider',
    'DiscoveredDevice',
    'KnownDeviceRecord',
    'MODULE_DECLARATION',
    'PointClass',
    'PointSnapshot',
    'DiscoveredDeviceCapabilitySummary',
    'RuntimeCapabilitySurvey',
    'ReconciliationOutcome',
    'ReconciliationOutcomeKind',
    'RemapCandidate',
    'SimulatedReadAdapter',
    'SimulatedWritableAdapter',
    'SupportPackDescriptor',
    'SupportPackLoadReport',
    'SupportPackLoadState',
    'SupportPackProbeResult',
    'SupportPackRegistration',
    'UnknownDiscoveredDeviceError',
    'DiscoveryProviderUnavailableError',
    'WorkbenchDescriptor',
    'discover_optional_support_pack_modules',
    'load_optional_support_packs',
    'SupportPackCapabilitySummary',
    'survey_runtime_capabilities',
]
