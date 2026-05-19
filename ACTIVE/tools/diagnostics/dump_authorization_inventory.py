from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.app import ShellBootstrapper, ShellController
    from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
    from universaldaq.profiles import ProfileSnapshot, WorkspaceState
    from universaldaq.security import ActorContext, RoleClass
    from universaldaq.ui import AuthoritySurface, GraphModeSession

    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-AUTH-DIAG'),
        workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW),
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=snapshot,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer-user'), role_class=RoleClass.OBSERVER, origin='local-shell'),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.submit_output_request(
        request_id=RequestId('REQ-AUTH-DIAG-001'),
        output_id=OutputId('OUT-AUTH-DIAG-001'),
        requested_value='5',
        actor=ActorId('observer-user'),
        requested_at=as_event_time(3),
        applied_value='5',
        observed_value='5',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-AUTH-DIAG-001'), timestamp=as_event_time(6))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-AUTH-DIAG-001'), actor=ActorId('observer-user'), timestamp=as_event_time(7))
    controller.export_review_artifact(
        export_id='EXP-AUTH-DIAG-001',
        manifest_id='MAN-AUTH-DIAG-001',
        actor=ActorId('observer-user'),
        timestamp=as_event_time(8),
    )

    payload = {
        'actor_id': str(controller.session.actor_context.actor_id),
        'role_class': controller.session.actor_context.role_class.value,
        'granted_permissions': list(controller.session.granted_permission_families),
        'last_authorization_action': controller.session.ui_session.last_authorization_action,
        'last_authorization_allowed': controller.session.ui_session.last_authorization_allowed,
        'last_authorization_reason': controller.session.ui_session.last_authorization_reason,
        'authorization_history_count': len(controller.session.authorization_history),
        'last_command_authorization_denied': controller.session.command_traces[-1].authorization_denied,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
