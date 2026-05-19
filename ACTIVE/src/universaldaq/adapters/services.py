from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, field

from universaldaq.common import EventTime, RuntimeMetricsStore

from .contracts import AdapterContract, DiscoveryProvider
from .errors import DiscoveryProviderUnavailableError, UnknownDiscoveredDeviceError
from .models import (
    AdapterCapability,
    AdapterCommandOutcome,
    AdapterCommandRequest,
    AdapterCommandResult,
    AdapterHealth,
    AdapterHealthState,
    AdapterPollResult,
    DeviceIdentity,
    DeviceLifecyclePhase,
    DiscoveredDevice,
    KnownDeviceRecord,
    PointSnapshot,
    SupportPackLoadReport,
    SupportPackRegistration,
    WorkbenchDescriptor,
)


@dataclass(slots=True)
class AdapterManagerService:
    adapters: dict[str, AdapterContract] = field(default_factory=dict)
    discovery_providers: dict[str, DiscoveryProvider] = field(default_factory=dict)
    support_packs: dict[str, SupportPackRegistration] = field(default_factory=dict)
    support_pack_load_reports: dict[str, SupportPackLoadReport] = field(default_factory=dict)
    discovered_devices: dict[str, DiscoveredDevice] = field(default_factory=dict)
    known_devices: dict[str, KnownDeviceRecord] = field(default_factory=dict)
    last_poll_results: dict[str, AdapterPollResult] = field(default_factory=dict)
    command_results: list[AdapterCommandResult] = field(default_factory=list)
    disconnected_adapter_ids: set[str] = field(default_factory=set)
    metrics: RuntimeMetricsStore | None = None

    def _tracked_call(self, *, counter_metric: str, timing_metric: str):
        if self.metrics is None:
            return nullcontext()
        self.metrics.increment(counter_metric)
        return self.metrics.measure(timing_metric)

    def register(self, adapter: AdapterContract) -> None:
        self.adapters[adapter.adapter_id] = adapter
        if self.metrics is not None:
            self.metrics.increment('adapters.register.calls')
            self.metrics.set_gauge('adapters.inventory.count', len(self.adapters))

    def register_discovery_provider(self, provider: DiscoveryProvider) -> None:
        self.discovery_providers[provider.provider_id] = provider
        if self.metrics is not None:
            self.metrics.increment('adapters.discovery_provider.register.calls')
            self.metrics.set_gauge('adapters.discovery_provider.count', len(self.discovery_providers))

    def install_support_pack(self, registration: SupportPackRegistration) -> None:
        self.support_packs[registration.descriptor.pack_id] = registration
        if self.metrics is not None:
            self.metrics.increment('adapters.support_pack.install.calls')
            self.metrics.set_gauge('adapters.support_pack.count', len(self.support_packs))
        for provider in registration.discovery_providers:
            if hasattr(provider, 'provider_id'):
                self.register_discovery_provider(provider)

    def record_support_pack_load_report(self, report: SupportPackLoadReport) -> None:
        self.support_pack_load_reports[report.pack_id] = report
        if self.metrics is not None:
            self.metrics.increment('adapters.support_pack.load_report.calls')
            self.metrics.set_gauge('adapters.support_pack.load_report.count', len(self.support_pack_load_reports))

    def support_pack_descriptors(self) -> tuple[str, ...]:
        return tuple(sorted(self.support_packs.keys()))

    def support_pack_load_inventory(self) -> tuple[SupportPackLoadReport, ...]:
        return tuple(self.support_pack_load_reports[pack_id] for pack_id in sorted(self.support_pack_load_reports.keys()))

    def adapter_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.adapters.keys()))

    def capability_inventory(self) -> tuple[AdapterCapability, ...]:
        return tuple(self.adapters[adapter_id].capability() for adapter_id in self.adapter_ids())

    def health_inventory(self) -> tuple[AdapterHealth, ...]:
        inventory = []
        for adapter_id in self.adapter_ids():
            if adapter_id in self.disconnected_adapter_ids:
                inventory.append(
                    AdapterHealth(
                        adapter_id=adapter_id,
                        state=AdapterHealthState.DISCONNECTED,
                        summary='adapter marked disconnected by lifecycle manager',
                    )
                )
                continue
            if adapter_id in self.last_poll_results and self.last_poll_results[adapter_id].health is not None:
                inventory.append(self.last_poll_results[adapter_id].health)
            else:
                inventory.append(self.adapters[adapter_id].health())
        return tuple(inventory)

    def poll_all(self, *, timestamp: EventTime) -> tuple[AdapterPollResult, ...]:
        results = []
        with self._tracked_call(counter_metric='adapters.poll_all.calls', timing_metric='adapters.poll_all.ms'):
            for adapter_id in self.adapter_ids():
                if adapter_id in self.disconnected_adapter_ids:
                    continue
                result = self.adapters[adapter_id].poll(timestamp=int(timestamp))
                self.last_poll_results[adapter_id] = result
                results.append(result)
        if self.metrics is not None:
            self.metrics.increment('adapters.poll_result.count', len(results))
            self.metrics.increment('adapters.snapshot.count', sum(len(item.snapshots) for item in results))
            self.metrics.set_gauge('adapters.last_poll_results.count', len(self.last_poll_results))
        return tuple(results)

    def poll_adapter(self, *, adapter_id: str, timestamp: EventTime, include_disconnected: bool = False) -> AdapterPollResult | None:
        adapter = self.adapters.get(adapter_id)
        if adapter is None:
            return None
        if adapter_id in self.disconnected_adapter_ids and not include_disconnected:
            return None
        with self._tracked_call(counter_metric='adapters.poll_single.calls', timing_metric='adapters.poll_single.ms'):
            result = adapter.poll(timestamp=int(timestamp))
        self.last_poll_results[adapter_id] = result
        if self.metrics is not None:
            self.metrics.increment('adapters.snapshot.count', len(result.snapshots))
            if include_disconnected:
                self.metrics.increment('adapters.recovery_poll.calls')
        return result

    def snapshots(self) -> tuple[PointSnapshot, ...]:
        rows: list[PointSnapshot] = []
        for result in self.last_poll_results.values():
            rows.extend(result.snapshots)
        return tuple(rows)

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        with self._tracked_call(counter_metric='adapters.submit_command.calls', timing_metric='adapters.submit_command.ms'):
            result = self._submit_command_impl(request)
        if self.metrics is not None:
            self.metrics.set_gauge('adapters.command_results.count', len(self.command_results))
        return result

    def _submit_command_impl(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        adapter = self.adapters.get(request.adapter_id)
        if adapter is None:
            result = AdapterCommandResult(
                request=request,
                outcome=AdapterCommandOutcome.TARGET_NOT_FOUND,
                reason='adapter not registered',
                health=AdapterHealth(
                    adapter_id=request.adapter_id,
                    state=AdapterHealthState.ERROR,
                    summary='adapter not registered',
                ),
            )
            self.command_results.append(result)
            return result
        if request.adapter_id in self.disconnected_adapter_ids:
            result = AdapterCommandResult(
                request=request,
                outcome=AdapterCommandOutcome.TRANSPORT_FAILED,
                reason='adapter currently disconnected',
                health=AdapterHealth(
                    adapter_id=request.adapter_id,
                    state=AdapterHealthState.DISCONNECTED,
                    summary='adapter currently disconnected',
                ),
            )
            self.command_results.append(result)
            return result
        result = adapter.submit_command(request)
        self.command_results.append(result)
        return result

    def discover_devices(self, *, timestamp: EventTime) -> tuple[DiscoveredDevice, ...]:
        with self._tracked_call(counter_metric='adapters.discover.calls', timing_metric='adapters.discover.ms'):
            discovered = self._discover_devices_impl(timestamp=timestamp)
        if self.metrics is not None:
            self.metrics.set_gauge('adapters.discovered_devices.count', len(discovered))
        self.discovered_devices = discovered
        return tuple(discovered[key] for key in sorted(discovered.keys()))

    def _discover_devices_impl(self, *, timestamp: EventTime) -> dict[str, DiscoveredDevice]:
        discovered: dict[str, DiscoveredDevice] = {}
        for provider_id in sorted(self.discovery_providers.keys()):
            provider = self.discovery_providers[provider_id]
            for device in provider.discover(timestamp=int(timestamp)):
                known = self.match_known_device(device.identity)
                if known is not None:
                    device = DiscoveredDevice(
                        device_key=device.device_key,
                        identity=device.identity,
                        provider_id=device.provider_id,
                        support_tier=device.support_tier,
                        capability_labels=device.capability_labels,
                        bound_adapter_id=device.bound_adapter_id,
                        workbenches=device.workbenches,
                        known_device_key=known.known_device_key,
                        metadata=device.metadata,
                    )
                discovered[device.device_key] = device
        return discovered

    def activate_discovered_device(self, *, device_key: str) -> tuple[DiscoveredDevice, str | None, tuple[WorkbenchDescriptor, ...]]:
        device = self.discovered_devices.get(device_key)
        if device is None:
            raise UnknownDiscoveredDeviceError(f'unknown discovered device: {device_key}')
        provider = self.discovery_providers.get(device.provider_id)
        if provider is None:
            raise DiscoveryProviderUnavailableError(f'discovery provider not registered: {device.provider_id}')
        adapter_id = device.bound_adapter_id
        if adapter_id is None:
            adapter = provider.activate(device)
            if adapter is not None:
                self.register(adapter)
                adapter_id = adapter.adapter_id
        workbenches = provider.workbenches(device)
        activated = DiscoveredDevice(
            device_key=device.device_key,
            identity=device.identity,
            provider_id=device.provider_id,
            support_tier=device.support_tier,
            capability_labels=device.capability_labels,
            bound_adapter_id=adapter_id,
            workbenches=workbenches,
            known_device_key=device.known_device_key,
            metadata=device.metadata,
        )
        self.discovered_devices[device_key] = activated
        if adapter_id is not None:
            self.disconnected_adapter_ids.discard(adapter_id)
            if self.metrics is not None:
                self.metrics.increment('adapters.activate_discovered.calls')
        return activated, adapter_id, workbenches

    def remember_known_device(
        self,
        *,
        identity: DeviceIdentity,
        timestamp: EventTime,
        profile_id: str | None = None,
    ) -> KnownDeviceRecord:
        record = KnownDeviceRecord(
            known_device_key=f'known::{identity.stable_key}',
            identity_key=identity.stable_key,
            display_name=identity.display_name,
            last_profile_id=profile_id,
            last_seen_at=timestamp,
            metadata={'transport': '' if identity.transport is None else identity.transport},
        )
        self.known_devices[identity.stable_key] = record
        if self.metrics is not None:
            self.metrics.increment('adapters.known_device.remember.calls')
            self.metrics.set_gauge('adapters.known_device.count', len(self.known_devices))
        return record

    def match_known_device(self, identity: DeviceIdentity) -> KnownDeviceRecord | None:
        return self.known_devices.get(identity.stable_key)

    def mark_adapter_disconnected(self, *, adapter_id: str) -> None:
        if adapter_id in self.adapters:
            self.disconnected_adapter_ids.add(adapter_id)
            if self.metrics is not None:
                self.metrics.increment('adapters.mark_disconnected.calls')
                self.metrics.set_gauge('adapters.disconnected.count', len(self.disconnected_adapter_ids))

    def reconnect_adapter(self, *, adapter_id: str) -> None:
        self.disconnected_adapter_ids.discard(adapter_id)
        if self.metrics is not None:
            self.metrics.increment('adapters.reconnect.calls')
            self.metrics.set_gauge('adapters.disconnected.count', len(self.disconnected_adapter_ids))

    def lifecycle_phase_for_device(self, *, device: DiscoveredDevice | None, active_adapter_id: str | None) -> DeviceLifecyclePhase:
        if device is None:
            return DeviceLifecyclePhase.NO_DEVICE
        if active_adapter_id is None:
            return DeviceLifecyclePhase.IDENTIFIED
        if active_adapter_id in self.disconnected_adapter_ids:
            return DeviceLifecyclePhase.DISCONNECTED
        return DeviceLifecyclePhase.READY_TO_CONFIGURE
