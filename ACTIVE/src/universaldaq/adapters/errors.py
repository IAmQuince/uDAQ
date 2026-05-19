from __future__ import annotations


class AdapterLifecycleError(LookupError):
    """Base class for adapter lifecycle lookup failures."""


class UnknownDiscoveredDeviceError(AdapterLifecycleError):
    """Raised when a requested discovered-device key is not present in the active inventory."""


class DiscoveryProviderUnavailableError(AdapterLifecycleError):
    """Raised when a discovered device references a provider that is no longer registered."""
