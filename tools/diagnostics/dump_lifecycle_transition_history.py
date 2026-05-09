from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
    from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, VariableId, as_event_time
    from universaldaq.profiles import ProfileSnapshot, WorkspaceState
    from universaldaq.security import ActorContext, RoleClass
    from universaldaq.signals import VariableDefinition, VariableSourceKind
    from universaldaq.ui import AuthoritySurface, GraphModeSession
    from universaldaq_labjack.models import LabJackProbeRow
    from universaldaq_labjack.plugin import build_support_pack_registration

    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-DIAG-TRANSITIONS'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('diagnostic-operator'), role_class=RoleClass.ENGINEER, origin='diagnostic-harness'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == '470001')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    point_key = next(
        point_key
        for point_key, definition in services.bindings.point_definitions.items()
        if definition.device_identity_key == device.identity.stable_key and definition.point_ref.point_id == 'analog_in_0'
    )
    controller.bind_logical_signal_to_point(
        logical_signal_id=SignalId('stack_voltage'),
        point_key=point_key,
        display_name='Stack Voltage',
        timestamp=as_event_time(5),
    )
    controller.register_variable_definition(
        definition=VariableDefinition(
            variable_id=VariableId('stack_voltage_copy'),
            display_name='Stack Voltage Copy',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId('stack_voltage'),),
        ),
        timestamp=as_event_time(6),
    )
    controller.begin_quick_start(timestamp=as_event_time(7))
    controller.mark_active_device_disconnected(timestamp=as_event_time(8))
    controller.reconnect_active_device(timestamp=as_event_time(9))
    bundle = controller.lifecycle_review_bundle()
    payload = {
        'transition_trace': bundle['transition_trace'],
        'incremental_runtime_summary': bundle['incremental_runtime_summary'],
        'active_device_key': bundle['active_device_key'],
        'phase': bundle['lifecycle_summary']['phase'],
        'binding_review_summary': bundle['binding_review_summary'],
        'variable_health_summary': bundle['variable_health_summary'],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
