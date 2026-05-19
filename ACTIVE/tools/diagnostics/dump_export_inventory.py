from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.app import ShellBootstrapper, ShellController
    from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, TraceId, as_event_time
    from universaldaq.profiles import ProfileSnapshot, WorkspaceState
    from universaldaq.ui import AuthoritySurface, GraphModeSession

    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-EXP-DIAG'),
        workspace_state=WorkspaceState(page='review', review_mode=GraphMode.HISTORY, visible_traces=(TraceId('SIG-EXP-001'),)),
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=snapshot,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.set_overlay(overlay_name='commands', visible=True, timestamp=as_event_time(3))
    controller.submit_output_request(
        request_id=RequestId('REQ-EXP-001'),
        output_id=OutputId('OUT-EXP-001'),
        requested_value='55',
        actor=ActorId('reviewer'),
        authorization_state=AuthorizationState.ALLOWED,
        requested_at=as_event_time(4),
        applied_value='55',
        observed_value='55',
        applied_at=as_event_time(5),
        observed_at=as_event_time(6),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-EXP-001'), timestamp=as_event_time(7))
    result = controller.export_review_artifact(
        export_id='EXPORT-INV-001',
        manifest_id='MAN-INV-001',
        actor=ActorId('reviewer'),
        timestamp=as_event_time(8),
        include_profiles=True,
        include_diagnostics=True,
        diagnostics=({'tool': 'dump_export_inventory', 'scope': 'review'},),
    )

    payload = {
        'export_id': result.export_intent.export_id,
        'manifest_id': result.manifest.manifest_id,
        'artifact_class': result.export_intent.artifact_class.value,
        'scope': result.manifest.scope_summary,
        'warning_count': len(result.warnings),
        'artifact_paths': [item.descriptor.relative_path for item in result.serialized_artifacts],
        'artifact_types': [item.descriptor.artifact_type for item in result.serialized_artifacts],
        'bundle_record_count': len(result.bundle.records),
        'source_counts': result.bundle.source_counts,
        'omission_notes': list(result.manifest.omission_notes),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
