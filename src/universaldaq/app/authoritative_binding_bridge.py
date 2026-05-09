from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from universaldaq.common import OutputId, SignalId

from .service_registry import ShellServiceRegistry


class BindingReadbackStatus(StrEnum):
    APPLIED = 'applied'
    STALE = 'stale'
    CONFLICT = 'conflict'
    UNAVAILABLE = 'unavailable'


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthoritativeBindingRow:
    row_id: str
    authority_kind: str
    direction: str
    logical_id: str
    logical_display_name: str
    source_endpoint: str
    destination_endpoint: str
    status: str
    binding_policy: str
    device_identity_key: str
    provenance_label: str
    engineering_units: str | None = None
    enabled: bool = True
    note: str = ''
    authority_source: str = 'ShellServiceRegistry.bindings'
    last_confirmed_timestamp: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthoritativeBindingInventory:
    device_identity_key: str
    rows: tuple[AuthoritativeBindingRow, ...]
    authority_source: str = 'ShellServiceRegistry.bindings'
    readback_available: bool = True

    @property
    def total_count(self) -> int:
        return len(self.rows)

    @property
    def signal_count(self) -> int:
        return sum(1 for row in self.rows if row.direction == 'device_input_to_internal_signal')

    @property
    def output_count(self) -> int:
        return sum(1 for row in self.rows if row.direction == 'internal_signal_to_device_output')

    @property
    def applied_count(self) -> int:
        return sum(1 for row in self.rows if row.status == BindingReadbackStatus.APPLIED.value)

    @property
    def degraded_count(self) -> int:
        return sum(1 for row in self.rows if row.status != BindingReadbackStatus.APPLIED.value)


@dataclass(frozen=True, slots=True)
class BackendBindingReadbackProvider:
    """Read-only backend seam for applied binding state.

    The provider intentionally exposes readback only. Draft edits and future apply
    operations must be modeled elsewhere so the shell cannot mistake local draft
    state for controller/backend authority.
    """

    services: ShellServiceRegistry

    def list_authoritative_bindings(self, *, device_identity_key: str) -> AuthoritativeBindingInventory:
        return build_authoritative_binding_inventory(services=self.services, device_identity_key=device_identity_key)



def _friendly_point_label(*, services: ShellServiceRegistry, point_key: str) -> str:
    point_definition = services.bindings.point_definitions.get(point_key)
    if point_definition is None:
        return point_key
    point_ref = point_definition.point_ref
    label = point_ref.display_name or point_ref.point_id
    return f'{point_definition.friendly_name} ({label})'



def _signal_display_name(*, services: ShellServiceRegistry, signal_id: SignalId) -> str:
    definition = services.signals.definitions.get(signal_id)
    if definition is None:
        return str(signal_id)
    return str(definition.display_name)



def _binding_readback_status(*, services: ShellServiceRegistry, point_key: str, device_identity_key: str) -> tuple[BindingReadbackStatus, bool, str]:
    point_definition = services.bindings.point_definitions.get(point_key)
    if point_definition is None:
        return (
            BindingReadbackStatus.UNAVAILABLE,
            False,
            'authoritative binding target is not present in the current projected point inventory',
        )
    if point_definition.device_identity_key != device_identity_key:
        return (
            BindingReadbackStatus.CONFLICT,
            bool(point_definition.enabled),
            'authoritative binding target resolves to a different device identity than the selected context',
        )
    if not point_definition.enabled:
        return (
            BindingReadbackStatus.STALE,
            False,
            'authoritative binding target exists but is disabled or stale in the projected point inventory',
        )
    return (
        BindingReadbackStatus.APPLIED,
        True,
        'authoritative runtime binding read from backend services',
    )



def build_authoritative_binding_inventory(
    *,
    services: ShellServiceRegistry,
    device_identity_key: str,
) -> AuthoritativeBindingInventory:
    rows: list[AuthoritativeBindingRow] = []

    for signal_id, binding in services.bindings.signal_bindings_for_device_identity(device_identity_key):
        point_definition = services.bindings.point_definitions.get(binding.source_point_key)
        engineering_units = None
        if point_definition is not None and point_definition.point_ref.units is not None:
            engineering_units = str(point_definition.point_ref.units)
        status, enabled, note = _binding_readback_status(
            services=services,
            point_key=binding.source_point_key,
            device_identity_key=device_identity_key,
        )
        rows.append(
            AuthoritativeBindingRow(
                row_id=f'signal::{signal_id}',
                authority_kind='backend_applied',
                direction='device_input_to_internal_signal',
                logical_id=str(signal_id),
                logical_display_name=_signal_display_name(services=services, signal_id=signal_id),
                source_endpoint=_friendly_point_label(services=services, point_key=binding.source_point_key),
                destination_endpoint='',
                status=status.value,
                binding_policy=binding.binding_policy.value,
                device_identity_key=device_identity_key,
                provenance_label=str(binding.metadata.get('friendly_name', binding.source_point_key)),
                engineering_units=engineering_units,
                enabled=enabled,
                note=note,
            )
        )

    for output_id, binding in services.bindings.output_bindings_for_device_identity(device_identity_key):
        point_definition = services.bindings.point_definitions.get(binding.target_point_key)
        engineering_units = None
        if point_definition is not None and point_definition.point_ref.units is not None:
            engineering_units = str(point_definition.point_ref.units)
        status, enabled, note = _binding_readback_status(
            services=services,
            point_key=binding.target_point_key,
            device_identity_key=device_identity_key,
        )
        rows.append(
            AuthoritativeBindingRow(
                row_id=f'output::{output_id}',
                authority_kind='backend_applied',
                direction='internal_signal_to_device_output',
                logical_id=str(output_id),
                logical_display_name=str(output_id),
                source_endpoint='',
                destination_endpoint=_friendly_point_label(services=services, point_key=binding.target_point_key),
                status=status.value,
                binding_policy=binding.binding_policy.value,
                device_identity_key=device_identity_key,
                provenance_label=str(binding.metadata.get('friendly_name', binding.target_point_key)),
                engineering_units=engineering_units,
                enabled=enabled,
                note=note.replace('binding target', 'output binding target'),
            )
        )

    rows.sort(key=lambda row: (row.direction, row.logical_id, row.source_endpoint, row.destination_endpoint))
    return AuthoritativeBindingInventory(device_identity_key=device_identity_key, rows=tuple(rows))


__all__ = [
    'AuthoritativeBindingInventory',
    'AuthoritativeBindingRow',
    'BackendBindingReadbackProvider',
    'BindingReadbackStatus',
    'build_authoritative_binding_inventory',
]
