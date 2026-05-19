from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.common import EventTime

from .models import DeviceSupportTier, SupportPackLoadState
from .services import AdapterManagerService


@dataclass(frozen=True, slots=True)
class SupportPackCapabilitySummary:
    pack_id: str
    state: str
    summary: str


@dataclass(frozen=True, slots=True)
class DiscoveredDeviceCapabilitySummary:
    device_key: str
    provider_id: str
    display_name: str
    support_tier: str
    transport: str | None
    activation_available: bool
    readable_point_count: int
    writable_point_count: int
    capability_mode: str
    identity_state: str
    read_state: str
    write_state: str
    limited_access_reason: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RuntimeCapabilitySurvey:
    support_packs: tuple[SupportPackCapabilitySummary, ...]
    devices: tuple[DiscoveredDeviceCapabilitySummary, ...]
    summary: str


def survey_runtime_capabilities(*, adapters: AdapterManagerService, timestamp: EventTime) -> RuntimeCapabilitySurvey:
    discovered = adapters.discover_devices(timestamp=timestamp)
    device_rows: list[DiscoveredDeviceCapabilitySummary] = []
    for device in discovered:
        adapter_id = device.bound_adapter_id
        capability = None if adapter_id is None else adapters.adapters.get(adapter_id)
        capability_inventory = None if capability is None else capability.capability()
        readable_point_count = 0 if capability_inventory is None else len(capability_inventory.readable_points)
        writable_point_count = 0 if capability_inventory is None else len(capability_inventory.writable_points)
        if device.support_tier == DeviceSupportTier.GENERIC:
            capability_mode = 'generic_baseline'
        elif device.support_tier == DeviceSupportTier.ENHANCED:
            capability_mode = 'enhanced_support_pack'
        else:
            capability_mode = 'protocol_family'
        activation_available = adapter_id is not None
        identity_state = 'known_identity' if any((device.identity.vendor, device.identity.model, device.identity.serial_number)) else 'generic_identity'
        if readable_point_count > 0:
            read_state = 'readable'
        elif activation_available:
            read_state = 'not_readable'
        else:
            read_state = 'unknown'
        if writable_point_count > 0:
            write_state = 'writable'
        elif activation_available:
            write_state = 'not_writable'
        else:
            write_state = 'unknown'
        limited_access_reason = None
        if not activation_available:
            limited_access_reason = 'device presence is known but no activation path is currently available'
        elif capability_mode == 'generic_baseline':
            limited_access_reason = 'running in generic baseline mode; richer protocol or vendor-specific semantics may require an optional support pack'
        elif capability_mode == 'protocol_family':
            limited_access_reason = 'protocol-family support is present, but device-specific enhancement details remain bounded'
        device_rows.append(
            DiscoveredDeviceCapabilitySummary(
                device_key=device.device_key,
                provider_id=device.provider_id,
                display_name=device.identity.display_name,
                support_tier=device.support_tier.value,
                transport=device.identity.transport,
                activation_available=activation_available,
                readable_point_count=readable_point_count,
                writable_point_count=writable_point_count,
                capability_mode=capability_mode,
                identity_state=identity_state,
                read_state=read_state,
                write_state=write_state,
                limited_access_reason=limited_access_reason,
                metadata={str(key): str(value) for key, value in device.identity.metadata.items()},
            )
        )
    pack_rows = tuple(
        SupportPackCapabilitySummary(
            pack_id=report.pack_id,
            state=report.state.value if isinstance(report.state, SupportPackLoadState) else str(report.state),
            summary=report.summary,
        )
        for report in adapters.support_pack_load_inventory()
    )
    if not pack_rows:
        summary = f'generic discovery available with {len(device_rows)} device(s); no optional support packs loaded'
    else:
        installed = sum(1 for item in pack_rows if item.state == SupportPackLoadState.INSTALLED.value)
        unavailable = sum(1 for item in pack_rows if item.state != SupportPackLoadState.INSTALLED.value)
        summary = f'capability survey found {len(device_rows)} device(s), {installed} installed support pack(s), {unavailable} limited or unavailable support pack(s)'
    return RuntimeCapabilitySurvey(support_packs=pack_rows, devices=tuple(device_rows), summary=summary)
