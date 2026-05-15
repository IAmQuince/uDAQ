from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
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
                probe_rows=(
                    LabJackProbeRow(
                        model='U6',
                        serial_number='470001',
                        transport='usb',
                        firmware_version='1.00',
                        hardware_revision='A',
                        connection_label='bench-u6',
                    ),
                )
            )
        )
    except Exception:
        pass

    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-DIAG'),
        workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=snapshot,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.discover_devices(timestamp=as_event_time(3))
    if controller.session.ui_session.detected_devices:
        active_key = controller.session.ui_session.detected_devices[0].device_key
        controller.select_detected_device(device_key=active_key, timestamp=as_event_time(4))
        controller.remember_active_device(timestamp=as_event_time(5))
        controller.begin_quick_start(timestamp=as_event_time(6))
        controller.mark_active_device_disconnected(timestamp=as_event_time(7))
        controller.reconnect_active_device(timestamp=as_event_time(8))
        controller.enter_advanced_setup(timestamp=as_event_time(9))
    poll_results = controller.poll_adapters(timestamp=as_event_time(10))
    controller.navigate(page='review', timestamp=as_event_time(11))
    controller.set_trace_visibility(trace_id=TraceId('SIG-001'), visible=True, timestamp=as_event_time(12))
    controller.set_overlay(overlay_name='alarms', visible=True, timestamp=as_event_time(13))
    controller.select_history_range(start=as_event_time(10), end=as_event_time(20), timestamp=as_event_time(14))
    controller.submit_output_request_via_adapter(
        request_id=RequestId('REQ-DIAG-001'),
        output_id=OutputId('OUT-DIAG-001'),
        adapter_id='SIM-WRITE-001',
        point_id='OUT-DIAG-001',
        requested_value='1',
        actor=ActorId('operator'),
        requested_at=as_event_time(15),
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(16),
        observed_at=as_event_time(17),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-DIAG'), timestamp=as_event_time(18))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-DIAG'), actor=ActorId('operator'), timestamp=as_event_time(19))
    result = controller.export_evidence_bundle(
        export_id='EXPORT-DIAG-001',
        bundle_id='BUNDLE-DIAG-001',
        manifest_id='MAN-DIAG-001',
        actor=ActorId('operator'),
        timestamp=as_event_time(20),
        include_profiles=True,
        include_diagnostics=True,
        diagnostics=(
            {
                'tool': 'dump_shell_state_inventory',
                'selected_range': [10, 20],
                'expected_records': 'mixed',
            },
        ),
    )
    controller.return_to_live(timestamp=as_event_time(21))

    payload = {
        'profile_id': str(controller.session.profile_snapshot.profile_id),
        'session_id': controller.session.session_id,
        'page': controller.session.current_page,
        'graph_mode': controller.session.ui_session.graph_session.mode.value,
        'authority': controller.session.ui_session.authority_surface.status_label,
        'actor_role_label': controller.session.ui_session.actor_role_label,
        'granted_capabilities': list(controller.session.ui_session.granted_capabilities),
        'last_authorization_action': controller.session.ui_session.last_authorization_action,
        'last_authorization_allowed': controller.session.ui_session.last_authorization_allowed,
        'last_authorization_reason': controller.session.ui_session.last_authorization_reason,
        'return_to_live_available': controller.session.ui_session.return_to_live_available,
        'visible_traces': [str(item) for item in controller.session.ui_session.workspace_state.visible_traces],
        'overlays': list(controller.session.ui_session.overlays),
        'selected_range': None if controller.session.ui_session.selected_range is None else list(controller.session.ui_session.selected_range),
        'last_restore_origin': None if controller.session.ui_session.last_restore_origin is None else controller.session.ui_session.last_restore_origin.value,
        'restore_machine_write_intent': controller.session.ui_session.restore_machine_write_intent,
        'adapter_ids': list(controller.services.adapters.adapter_ids()),
        'adapter_poll_count': len(poll_results),
        'adapter_snapshot_count': sum(len(item.snapshots) for item in poll_results),
        'device_phase': controller.session.ui_session.device_lifecycle_phase.value,
        'detected_device_count': len(controller.session.ui_session.detected_devices),
        'active_device': None if controller.session.ui_session.active_device is None else controller.session.ui_session.active_device.display_name,
        'active_adapter_id': controller.session.ui_session.active_adapter_id,
        'onboarding_mode': controller.session.ui_session.onboarding_mode,
        'known_device_restore_offer': controller.session.ui_session.known_device_restore_offer,
        'available_workbenches': [item.display_name for item in controller.session.ui_session.available_workbenches],
        'command_trace_count': len(controller.session.command_traces),
        'alarm_lifecycle_count': len(controller.session.alarm_lifecycles),
        'shell_evidence_count': len(controller.session.shell_evidence_records),
        'bundle_count': len(controller.session.evidence_bundle_ids),
        'bundle_ids': list(controller.session.evidence_bundle_ids),
        'last_bundle_id': controller.session.last_bundle_id,
        'last_manifest_id': controller.session.last_manifest_id,
        'last_export_manifest_id': controller.session.last_manifest_id,
        'last_export_summary': controller.session.last_export_summary,
        'result_manifest_id': result.manifest.manifest_id,
        'result_warning_count': len(result.warnings),
        'serialized_artifact_paths': [item.descriptor.relative_path for item in result.serialized_artifacts],
        'export_history_ids': list(controller.session.export_history_ids),
        'runtime_performance': controller.services.runtime_metrics.snapshot(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
