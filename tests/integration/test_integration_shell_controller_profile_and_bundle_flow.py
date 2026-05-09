from __future__ import annotations

import pytest

from universaldaq.app import AUTOSAVE_PROFILE_ID, ShellBootstrapper, ShellController
from universaldaq.common import AuthorizationState, GraphMode, ProfileId, RestoreOrigin, TraceId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-005', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-PROF-001', 'UDQ-REQ-HIS-001', 'UDQ-REQ-UI-007'], 'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-STATE-003', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'controller profile/autosave and bundle flow'}
pytestmark = pytest.mark.integration


def test_controller_profile_autosave_restore_and_bundle_flow():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-INT-CTRL-001'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.navigate(page='service', timestamp=as_event_time(3))
    controller.set_trace_visibility(trace_id=TraceId('SIG-200'), visible=True, timestamp=as_event_time(4))
    controller.save_profile(profile_id=ProfileId('PROF-USER-001'), timestamp=as_event_time(5))
    controller.save_autosave(timestamp=as_event_time(6))
    controller.navigate(page='review', timestamp=as_event_time(7))
    controller.restore_profile(profile_id=AUTOSAVE_PROFILE_ID, origin=RestoreOrigin.AUTOSAVE, timestamp=as_event_time(8))
    bundle = controller.build_evidence_bundle(bundle_id='BUNDLE-INT-CTRL-001')
    vm = controller.view_model()

    assert controller.services.profiles.load(ProfileId('PROF-USER-001')).workspace_state.page == 'service'
    assert controller.services.profiles.load(AUTOSAVE_PROFILE_ID).workspace_state.page == 'service'
    assert controller.session.ui_session.workspace_state.page == 'service'
    assert controller.session.ui_session.restore_profile_id == AUTOSAVE_PROFILE_ID
    assert vm.last_restore_origin == 'autosave'
    assert vm.restore_is_safe is True
    assert bundle.bundle_id in controller.session.evidence_bundle_ids
