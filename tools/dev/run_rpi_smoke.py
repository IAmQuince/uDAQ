from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--host-id', default='rpi-smoke-001')
    parser.add_argument('--model', default='5')
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
    from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, as_event_time
    from universaldaq.profiles import ProfileSnapshot, WorkspaceState
    from universaldaq.security import ActorContext, RoleClass
    from universaldaq.ui import AuthoritySurface, GraphModeSession
    from universaldaq_rpi.models import RaspberryPiProbeRow
    from universaldaq_rpi.plugin import build_support_pack_registration

    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(RaspberryPiProbeRow(model=args.model, host_id=args.host_id, enable_gpio=True),)
        )
    )
    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-RPI-SMOKE'),
        workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE),
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=snapshot,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('rpi-smoke'), role_class=RoleClass.ENGINEER, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    devices = controller.discover_devices(timestamp=as_event_time(3))
    device = next((item for item in devices if item.identity.serial_number == args.host_id), None)
    if device is None:
        print('rpi-smoke: no Raspberry Pi device discovered')
        return 2
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    controller.bind_logical_signal_to_point(logical_signal_id=SignalId('rpi_cpu_temp'), point_key=f'{controller.session.ui_session.active_adapter_id}:host_cpu_temp_c', timestamp=as_event_time(5))
    controller.begin_quick_start(timestamp=as_event_time(6))
    review_bundle = controller.lifecycle_review_bundle()
    print(
        'rpi-smoke:'
        f' active_adapter={controller.session.ui_session.active_adapter_id}'
        f' phase={controller.session.ui_session.device_lifecycle_phase.value}'
        f' projected_points={review_bundle["lifecycle_summary"]["projected_point_count"]}'
        f' published_signals={review_bundle["lifecycle_summary"]["published_signal_count"]}'
        f' highlighted_bindings={len(review_bundle["binding_review_summary"]["highlighted_items"])}'
        f' variable_total={review_bundle["variable_health_summary"]["total_variable_count"]}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
