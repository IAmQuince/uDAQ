from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import sleep
from typing import Iterable

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, VariableId, SignalQuality, AlarmId, as_event_time
from universaldaq.events import AlarmDefinition
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.signals import VariableDefinition, VariableSourceKind, VariableState
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration


@dataclass(frozen=True, slots=True)
class U6PreparedController:
    controller: ShellController
    active_adapter_id: str
    signal_ids: tuple[SignalId, ...]
    variable_ids: tuple[VariableId, ...]


def build_services(*, journal_path: Path | None = None):
    services = build_default_service_registry()
    if journal_path is not None:
        services.runtime_quality.journal.file_path = journal_path
    return services


def install_labjack_support_pack(
    services,
    *,
    real_hardware: bool,
    serial_number: str | None = None,
    simulated_serial_number: str = '470055',
    probe_rows: tuple[LabJackProbeRow, ...] = (),
    auto_probe_real_hardware: bool | None = None,
    real_backend_factory=None,
) -> None:
    effective_probe_rows = probe_rows if real_hardware else (LabJackProbeRow(model='U6', serial_number=simulated_serial_number, transport='usb'),)
    registration = build_support_pack_registration(
        probe_rows=effective_probe_rows,
        prefer_real_hardware=real_hardware,
        auto_probe_real_hardware=real_hardware if auto_probe_real_hardware is None else auto_probe_real_hardware,
        requested_serial_number=serial_number,
        real_backend_factory=real_backend_factory,
    )
    services.adapters.install_support_pack(registration)


def bootstrap_controller(*, services, profile_id: str, actor_id: str) -> ShellController:
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId(profile_id),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId(actor_id), role_class=RoleClass.ENGINEER, origin='local-shell'),
        services=services,
    )
    return ShellController.from_bootstrapped_shell(boot)


def _point_key_for(device_identity_key: str, point_id: str, point_definitions: dict[str, object]) -> str:
    for point_key, definition in point_definitions.items():
        if definition.device_identity_key == device_identity_key and definition.point_ref.point_id == point_id:
            return point_key
    raise LookupError(f'point_id not projected: {point_id}')


def prepare_u6_live_value_slice(
    controller: ShellController,
    *,
    timestamp_start: int = 3,
) -> U6PreparedController:
    devices = controller.discover_devices(timestamp=as_event_time(timestamp_start))
    device = next((item for item in devices if 'LabJack U6' in item.display_name), None)
    if device is None:
        raise RuntimeError('no LabJack U6 device discovered')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(timestamp_start + 1))
    active_adapter_id = controller.session.ui_session.active_adapter_id
    if active_adapter_id is None:
        raise RuntimeError('U6 activation did not produce an active adapter')

    signal_specs = (
        (SignalId('live_input_a'), 'analog_in_0', 'Live Input A'),
        (SignalId('live_input_b'), 'analog_in_1', 'Live Input B'),
        (SignalId('live_input_c'), 'analog_in_2', 'Live Input C'),
    )
    for offset, (signal_id, point_id, display_name) in enumerate(signal_specs, start=2):
        controller.bind_logical_signal_to_point(
            logical_signal_id=signal_id,
            point_key=_point_key_for(device.identity.stable_key, point_id, controller.services.bindings.point_definitions),
            display_name=display_name,
            timestamp=as_event_time(timestamp_start + offset),
        )

    variable_defs = (
        VariableDefinition(
            variable_id=VariableId('mon_input_a'),
            display_name='Monitored Input A',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId('live_input_a'),),
            engineering_units='V',
        ),
        VariableDefinition(
            variable_id=VariableId('delta_ab'),
            display_name='Input Delta A-B',
            source_kind=VariableSourceKind.EXPRESSION,
            signal_dependencies=(SignalId('live_input_a'), SignalId('live_input_b')),
            engineering_units='V',
            expression='a - b',
            dependency_aliases={
                'live_input_a': 'a',
                'live_input_b': 'b',
            },
        ),
        VariableDefinition(
            variable_id=VariableId('avg_abc'),
            display_name='Average Input',
            source_kind=VariableSourceKind.EXPRESSION,
            signal_dependencies=(SignalId('live_input_a'), SignalId('live_input_b'), SignalId('live_input_c')),
            engineering_units='V',
            expression='(a + b + c) / 3',
            dependency_aliases={
                'live_input_a': 'a',
                'live_input_b': 'b',
                'live_input_c': 'c',
            },
        ),
        VariableDefinition(
            variable_id=VariableId('avg_nonnegative'),
            display_name='Average Nonnegative',
            source_kind=VariableSourceKind.EXPRESSION,
            variable_dependencies=(VariableId('avg_abc'),),
            expression='avg >= 0',
            dependency_aliases={'avg_abc': 'avg'},
        ),
    )
    register_base = timestamp_start + 8
    for index, definition in enumerate(variable_defs):
        controller.register_variable_definition(definition=definition, timestamp=as_event_time(register_base + index))

    controller.services.events.register_alarm_definition(
        AlarmDefinition(
            alarm_id=AlarmId('ALM-U6-AVG-DEGRADED'),
            summary='Average input degraded',
            severity='warning',
            source_kind='variable',
            source_id='avg_abc',
            variable_id=VariableId('avg_abc'),
            condition_kind='variable_state',
            trigger_states=(VariableState.DEGRADED, VariableState.STALE, VariableState.UNRESOLVED),
            trigger_qualities=(SignalQuality.DISCONNECTED, SignalQuality.STALE, SignalQuality.INVALID),
            tags=('u6', 'bounded-live-value'),
        )
    )
    controller.begin_quick_start(timestamp=as_event_time(register_base + len(variable_defs) + 1))
    controller.poll_adapters(timestamp=as_event_time(register_base + len(variable_defs) + 2))
    return U6PreparedController(
        controller=controller,
        active_adapter_id=active_adapter_id,
        signal_ids=tuple(item[0] for item in signal_specs),
        variable_ids=tuple(definition.variable_id for definition in variable_defs),
    )


def run_poll_cycles(
    controller: ShellController,
    *,
    timestamp_start: int,
    cycles: int,
    cycle_delay_seconds: float = 0.0,
) -> None:
    current = timestamp_start
    for index in range(max(0, cycles)):
        controller.poll_adapters(timestamp=as_event_time(current))
        current += 1
        if cycle_delay_seconds > 0 and index < max(0, cycles) - 1:
            sleep(cycle_delay_seconds)


def summarize_discovered_devices(controller: ShellController) -> tuple[dict[str, str], ...]:
    rows: list[dict[str, str]] = []
    for device in controller.session.ui_session.detected_devices:
        rows.append(
            {
                'device_key': device.device_key,
                'display_name': device.display_name,
                'provider_id': device.provider_id,
                'serial_number': '' if device.identity.serial_number is None else device.identity.serial_number,
                'transport': device.identity.transport,
            }
        )
    return tuple(rows)


def format_key_values(items: Iterable[tuple[str, object]]) -> str:
    return '\n'.join(f'{key}: {value}' for key, value in items)
