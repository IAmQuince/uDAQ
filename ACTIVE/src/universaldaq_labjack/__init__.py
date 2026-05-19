"""Optional LabJack support pack for UniversalDAQ.

This package is intentionally separate from the universaldaq core package so the
core can remain vendor-agnostic. Installing or importing this package enhances
support for LabJack-family devices but is not required for the base application
or generic/manual device workflows.
"""

from .discovery import LabJackU6DiscoveryProvider
from .models import LabJackAdapterStatusSnapshot, LabJackProbeRow
from .plugin import build_support_pack_registration, probe_support_pack
from .real_u6 import RealLabJackU6Adapter, probe_real_u6_row
from .simulated_u6 import SimulatedLabJackU6Adapter

__all__ = [
    'LabJackAdapterStatusSnapshot',
    'LabJackProbeRow',
    'LabJackU6DiscoveryProvider',
    'RealLabJackU6Adapter',
    'SimulatedLabJackU6Adapter',
    'build_support_pack_registration',
    'probe_real_u6_row',
    'probe_support_pack',
]
