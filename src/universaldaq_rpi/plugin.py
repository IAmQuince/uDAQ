from __future__ import annotations

from universaldaq.adapters import DeviceSupportTier, SupportPackDescriptor, SupportPackProbeResult, SupportPackRegistration

from .discovery import RaspberryPiDiscoveryProvider
from .models import RaspberryPiProbeRow


def _descriptor() -> SupportPackDescriptor:
    return SupportPackDescriptor(
        pack_id='universaldaq_rpi',
        display_name='UniversalDAQ Raspberry Pi Support Pack',
        plugin_module='universaldaq_rpi',
        support_tier=DeviceSupportTier.PROTOCOL_FAMILY,
        enhancement_only=False,
        provides_driver_bridge=False,
        dependency_hints=(),
        transport_hints=('local', 'gpio'),
        adapter_family='local_platform',
        metadata={'vendor': 'Raspberry Pi', 'models': '4B/5 reference local platform', 'real_hardware_ready': 'false'},
    )


def probe_support_pack() -> SupportPackProbeResult:
    return SupportPackProbeResult(
        descriptor=_descriptor(),
        available=True,
        summary='support pack available with built-in local platform reference surface',
        metadata={'dependencies': 'stdlib-only'},
    )


def build_support_pack_registration(*, probe_rows: tuple[RaspberryPiProbeRow, ...] = ()) -> SupportPackRegistration:
    provider = RaspberryPiDiscoveryProvider(probe_rows=probe_rows)
    return SupportPackRegistration(descriptor=_descriptor(), discovery_providers=(provider,))
