from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
    from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, TraceId, as_event_time
    from universaldaq.profiles import ProfileSnapshot, WorkspaceState
    from universaldaq.security import ActorContext, RoleClass
    from universaldaq.ui import AuthoritySurface, GraphModeSession

    services = build_default_service_registry()
    try:
        from universaldaq_labjack.models import LabJackProbeRow
        from universaldaq_labjack.plugin import build_support_pack_registration

        services.adapters.install_support_pack(
            build_support_pack_registration(
                probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
            )
        )
    except Exception:
        pass

    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-SMOKE'),
        workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=snapshot,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer-smoke'), role_class=RoleClass.OBSERVER, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.discover_devices(timestamp=as_event_time(3))
    if controller.session.ui_session.detected_devices:
        u6_device = next((item for item in controller.session.ui_session.detected_devices if 'LabJack U6' in item.display_name), None)
        if u6_device is not None:
            controller.select_detected_device(device_key=u6_device.device_key, timestamp=as_event_time(4))
            controller.begin_quick_start(timestamp=as_event_time(5))
            controller.remember_active_device(timestamp=as_event_time(6))
    controller.navigate(page='review', timestamp=as_event_time(7))
    controller.poll_adapters(timestamp=as_event_time(7))
    controller.set_trace_visibility(trace_id=TraceId('SIG-SMOKE'), visible=True, timestamp=as_event_time(8))
    denied_command = controller.submit_output_request_via_adapter(
        request_id=RequestId('REQ-SMOKE-001'),
        output_id=OutputId('OUT-SMOKE-001'),
        adapter_id='SIM-WRITE-001',
        point_id='OUT-SMOKE-001',
        requested_value='1',
        actor=ActorId('observer-smoke'),
        requested_at=as_event_time(9),
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(10),
        observed_at=as_event_time(11),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-SMOKE-001'), timestamp=as_event_time(12))
    denied_ack = controller.acknowledge_alarm(alarm_id=AlarmId('ALM-SMOKE-001'), actor=ActorId('observer-smoke'), timestamp=as_event_time(13))
    result = controller.export_review_artifact(
        export_id='EXPORT-SMOKE-001',
        manifest_id='MAN-SMOKE-001',
        actor=ActorId('observer-smoke'),
        timestamp=as_event_time(14),
    )
    controller.return_to_live(timestamp=as_event_time(15))
    print(
        f'shell-smoke: profile={controller.session.profile_snapshot.profile_id} '
        f'page={controller.session.ui_session.workspace_state.page} '
        f'mode={controller.session.ui_session.graph_session.mode.value} '
        f'device_phase={controller.session.ui_session.device_lifecycle_phase.value} '
        f'detected={len(controller.session.ui_session.detected_devices)} '
        f'command_allowed={denied_command.session.command_traces[-1].authorization_denied is False} '
        f'ack_states={denied_ack.session.alarm_lifecycles[-1].ordered_states} '
        f'manifest={result.manifest.manifest_id}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
