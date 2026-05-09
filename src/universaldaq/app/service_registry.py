from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from universaldaq.adapters import (
    AdapterInventoryDiscoveryProvider,
    AdapterManagerService,
    DeviceRegistryService,
    SimulatedReadAdapter,
    SimulatedWritableAdapter,
    load_optional_support_packs,
)
from universaldaq.automation import GovernedActionClaimService
from universaldaq.commands import CommandAdmissionService
from universaldaq.common import RuntimeMetricsStore
from universaldaq.events.services import AlarmLifecycleService
from universaldaq.historian.services import EvidenceBundleService
from universaldaq.runtime import RuntimeQualityService
from universaldaq.outputs.services import OutputCommandService
from universaldaq.profiles.store import InMemoryBenchStateStore, InMemoryProfileStore
from universaldaq.rules import RuleEvaluationService
from universaldaq.sequences import SequenceService
from universaldaq.security import AuthorizationService
from universaldaq.signals import SignalBindingService, SignalRegistry, VariableEvaluationService


@dataclass(frozen=True, slots=True, kw_only=True)
class ShellServiceRegistry:
    signals: SignalRegistry
    commands: CommandAdmissionService
    outputs: OutputCommandService
    events: AlarmLifecycleService
    profiles: InMemoryProfileStore
    bench_state: InMemoryBenchStateStore
    rules: RuleEvaluationService
    sequences: SequenceService
    claims: GovernedActionClaimService
    historian: EvidenceBundleService
    security: AuthorizationService
    adapters: AdapterManagerService
    bindings: SignalBindingService
    variables: VariableEvaluationService
    device_registry: DeviceRegistryService
    runtime_metrics: RuntimeMetricsStore
    runtime_quality: RuntimeQualityService


def build_default_service_registry(*, load_support_packs: bool = True, support_pack_module_names: Iterable[str] | None = None) -> ShellServiceRegistry:
    metrics = RuntimeMetricsStore()
    adapters = AdapterManagerService(metrics=metrics)
    signals = SignalRegistry(metrics=metrics)
    bindings = SignalBindingService(metrics=metrics)
    variables = VariableEvaluationService(metrics=metrics)
    device_registry = DeviceRegistryService(metrics=metrics)
    adapters.register(
        SimulatedReadAdapter.from_values(
            adapter_id='SIM-READ-001',
            values={
                'PT-101': ('100.0', '100.0', 'psi'),
                'TT-201': ('42.0', '42.0', 'degC'),
            },
            timestamp=1,
        )
    )
    adapters.register(
        SimulatedWritableAdapter(
            adapter_id='SIM-WRITE-001',
            writable_points={'OUT-SMOKE-001': '0', 'OUT-DIAG-001': '0', 'OUT-ADAPT-001': '0'},
            observed_points={'OUT-SMOKE-001': '0', 'OUT-DIAG-001': '0', 'OUT-ADAPT-001': '0'},
        )
    )
    adapters.register_discovery_provider(
        AdapterInventoryDiscoveryProvider(
            provider_id='generic_adapter_inventory',
            capability_inventory_getter=adapters.capability_inventory,
            adapter_getter=lambda adapter_id: adapters.adapters.get(adapter_id),
        )
    )
    if load_support_packs:
        load_optional_support_packs(adapters, module_names=support_pack_module_names)
    runtime_quality = RuntimeQualityService(metrics=metrics)
    return ShellServiceRegistry(
        signals=signals,
        bindings=bindings,
        variables=variables,
        commands=CommandAdmissionService(metrics=metrics),
        outputs=OutputCommandService(),
        events=AlarmLifecycleService(),
        profiles=InMemoryProfileStore(),
        bench_state=InMemoryBenchStateStore(),
        rules=RuleEvaluationService(),
        sequences=SequenceService(),
        claims=GovernedActionClaimService(),
        historian=EvidenceBundleService(),
        security=AuthorizationService.from_default_policy(),
        adapters=adapters,
        device_registry=device_registry,
        runtime_metrics=metrics,
        runtime_quality=runtime_quality,
    )
