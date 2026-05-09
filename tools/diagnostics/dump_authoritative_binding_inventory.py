from __future__ import annotations

from dataclasses import asdict
import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.app import (
        ShellBootstrapper,
        ShellController,
        build_authoritative_binding_inventory,
        build_default_service_registry,
    )
    from universaldaq.common import ActorId, AuthorizationState, GraphMode, OutputId, ProfileId, as_event_time
    from universaldaq.profiles import ProfileSnapshot, WorkspaceState
    from universaldaq.security import ActorContext, RoleClass
    from universaldaq.signals import BindingPolicy, LogicalOutputBinding
    from universaldaq.ui import AuthoritySurface, GraphModeSession

    services = build_default_service_registry(load_support_packs=False)
    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-APPLIED-BRIDGE'),
        workspace_state=WorkspaceState(page='system', review_mode=GraphMode.LIVE),
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=snapshot,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('bridge-reviewer'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.discover_devices(timestamp=as_event_time(3))
    devices = controller.session.ui_session.detected_devices
    inventory = None
    if devices:
        controller.select_detected_device(device_key=devices[0].device_key, timestamp=as_event_time(4))
        controller.begin_quick_start(timestamp=as_event_time(5))
        active_device = controller.session.ui_session.active_device
        if active_device is not None:
            writable = services.bindings.point_definitions_for_device(active_device.identity.stable_key)
            target = next((item for item in writable if item.point_ref.point_class.value != 'status'), None)
            if target is not None:
                services.bindings.bind_output(
                    LogicalOutputBinding(
                        logical_output_id=OutputId('OUT-DEMO-001'),
                        target_point_key=target.stable_point_key,
                        binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
                        metadata={
                            'device_identity_key': active_device.identity.stable_key,
                            'point_id': target.point_ref.point_id,
                            'friendly_name': target.friendly_name,
                        },
                    )
                )
            inventory = build_authoritative_binding_inventory(
                services=services,
                device_identity_key=active_device.identity.stable_key,
            )

    payload = {
        'authoritative_inventory': None if inventory is None else {
            'device_identity_key': inventory.device_identity_key,
            'total_count': inventory.total_count,
            'signal_count': inventory.signal_count,
            'output_count': inventory.output_count,
            'rows': [asdict(row) for row in inventory.rows],
        },
        'note': 'Applied bindings are backend-authoritative read models. Shell drafts remain non-authoritative until controller-backed apply is implemented.',
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
