from __future__ import annotations

from universaldaq.adapters import DeviceSupportTier, SupportPackDescriptor, SupportPackProbeResult, SupportPackRegistration

from .discovery import LabJackU6DiscoveryProvider, probe_driver_status
from .models import LabJackProbeRow
from .real_u6 import BackendFactory


def _descriptor(*, real_hardware_ready: bool) -> SupportPackDescriptor:
    return SupportPackDescriptor(
        pack_id='universaldaq_labjack',
        display_name='UniversalDAQ LabJack Support Pack',
        plugin_module='universaldaq_labjack',
        support_tier=DeviceSupportTier.ENHANCED,
        enhancement_only=False,
        provides_driver_bridge=True,
        dependency_hints=('u6', 'labjack.ljm'),
        transport_hints=('usb',),
        adapter_family='vendor_driver',
        metadata={
            'vendor': 'LabJack',
            'models': 'U6 pilot',
            'real_hardware_ready': str(real_hardware_ready).lower(),
        },
    )


def probe_support_pack() -> SupportPackProbeResult:
    driver_available, driver_name = probe_driver_status()
    return SupportPackProbeResult(
        descriptor=_descriptor(real_hardware_ready=driver_available),
        available=True,
        summary='support pack available; real hardware path depends on LabJack driver availability',
        metadata={'driver_available': str(driver_available).lower(), 'driver_name': driver_name},
    )


def build_support_pack_registration(
    *,
    probe_rows: tuple[LabJackProbeRow, ...] = (),
    prefer_real_hardware: bool = False,
    auto_probe_real_hardware: bool = False,
    requested_serial_number: str | None = None,
    real_backend_factory: BackendFactory | None = None,
) -> SupportPackRegistration:
    provider = LabJackU6DiscoveryProvider(
        probe_rows=probe_rows,
        prefer_real_hardware=prefer_real_hardware,
        auto_probe_real_hardware=auto_probe_real_hardware,
        requested_serial_number=requested_serial_number,
        real_backend_factory=real_backend_factory,
    )
    descriptor = _descriptor(real_hardware_ready=prefer_real_hardware or auto_probe_real_hardware)
    return SupportPackRegistration(descriptor=descriptor, discovery_providers=(provider,))
