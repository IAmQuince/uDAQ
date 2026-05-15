from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Dump a machine-readable lifecycle review bundle for the current bounded vertical-slice harness.')
    parser.add_argument('--output', required=True, help='Path to write the JSON lifecycle review bundle.')
    parser.add_argument('--serial-number', default='470001', help='Simulated LabJack U6 serial number for the review harness.')
    parser.add_argument('--bind-signal-id', default='stack_voltage', help='Logical signal id to bind for the harness flow.')
    parser.add_argument('--variable-id', default='stack_voltage_copy', help='Variable id to define for the harness flow.')
    return parser


def main() -> int:
    args = build_parser().parse_args()
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number=args.serial_number, transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-DIAG-LIFECYCLE'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('diagnostic-operator'), role_class=RoleClass.ENGINEER, origin='diagnostic-harness'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == args.serial_number)
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    point_key = next(
        point_key
        for point_key, definition in services.bindings.point_definitions.items()
        if definition.device_identity_key == device.identity.stable_key and definition.point_ref.point_id == 'analog_in_0'
    )
    controller.bind_logical_signal_to_point(
        logical_signal_id=SignalId(args.bind_signal_id),
        point_key=point_key,
        display_name='Diagnostic Bound Signal',
        timestamp=as_event_time(5),
    )
    controller.register_variable_definition(
        definition=VariableDefinition(
            variable_id=VariableId(args.variable_id),
            display_name='Diagnostic Variable',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId(args.bind_signal_id),),
        ),
        timestamp=as_event_time(6),
    )
    controller.begin_quick_start(timestamp=as_event_time(7))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(controller.lifecycle_review_bundle(), indent=2), encoding='utf-8')
    print(output_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
