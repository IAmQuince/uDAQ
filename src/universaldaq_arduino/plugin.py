from __future__ import annotations

from universaldaq.adapters import DeviceSupportTier, SupportPackDescriptor, SupportPackProbeResult, SupportPackRegistration

from .discovery import ArduinoSerialDiscoveryProvider
from .models import ArduinoProbeRow


def _descriptor() -> SupportPackDescriptor:
    return SupportPackDescriptor(
        pack_id='universaldaq_arduino',
        display_name='UniversalDAQ Arduino Support Pack',
        plugin_module='universaldaq_arduino',
        support_tier=DeviceSupportTier.PROTOCOL_FAMILY,
        enhancement_only=False,
        provides_driver_bridge=False,
        dependency_hints=(),
        transport_hints=('serial',),
        adapter_family='microcontroller_serial',
        metadata={'vendor': 'Arduino', 'boards': 'Uno/Nano/Mega reference protocol', 'real_hardware_ready': 'false'},
    )


def probe_support_pack() -> SupportPackProbeResult:
    return SupportPackProbeResult(
        descriptor=_descriptor(),
        available=True,
        summary='support pack available with built-in reference serial protocol surface',
        metadata={'dependencies': 'stdlib-only'},
    )


def build_support_pack_registration(*, probe_rows: tuple[ArduinoProbeRow, ...] = ()) -> SupportPackRegistration:
    provider = ArduinoSerialDiscoveryProvider(probe_rows=probe_rows)
    return SupportPackRegistration(descriptor=_descriptor(), discovery_providers=(provider,))
