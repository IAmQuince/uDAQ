from __future__ import annotations

import pytest

from universaldaq.app import AUTOSAVE_PROFILE_ID, ShellBootstrapper, ShellController
from universaldaq.common import AuthorizationState, GraphMode, ProfileId, RestoreOrigin, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-007', 'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-PROF-002', 'UDQ-REQ-ARCH-002'], 'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-TRANS-002', 'UDQ-INV-EVID-003'], 'worked_example_reference': None, 'expected_proof_output': 'restore-origin metadata with no machine write intent'}
pytestmark = pytest.mark.contract


def test_restore_origin_metadata_survives_shell_restore():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-CON-RESTORE-001'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.REVIEW),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.save_autosave(timestamp=as_event_time(3))
    controller.restore_profile(profile_id=AUTOSAVE_PROFILE_ID, origin=RestoreOrigin.AUTOSAVE, timestamp=as_event_time(4))

    assert controller.session.restore_result.origin == RestoreOrigin.AUTOSAVE
    assert controller.session.ui_session.last_restore_origin == RestoreOrigin.AUTOSAVE
    assert controller.session.restore_result.machine_write_intent is False
    assert controller.session.ui_session.restore_machine_write_intent is False
    assert controller.session.restore_result.profile_id == AUTOSAVE_PROFILE_ID
