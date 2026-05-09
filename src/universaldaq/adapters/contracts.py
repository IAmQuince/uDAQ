from __future__ import annotations

from typing import Protocol

from .models import AdapterCapability, AdapterCommandRequest, AdapterCommandResult, AdapterHealth, AdapterPollResult, DiscoveredDevice, WorkbenchDescriptor


class AdapterContract(Protocol):
    adapter_id: str

    def capability(self) -> AdapterCapability:
        ...

    def health(self) -> AdapterHealth:
        ...

    def poll(self, *, timestamp: int) -> AdapterPollResult:
        ...

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        ...


class DiscoveryProvider(Protocol):
    provider_id: str

    def discover(self, *, timestamp: int) -> tuple[DiscoveredDevice, ...]:
        ...

    def activate(self, device: DiscoveredDevice) -> AdapterContract | None:
        ...

    def workbenches(self, device: DiscoveredDevice) -> tuple[WorkbenchDescriptor, ...]:
        ...
