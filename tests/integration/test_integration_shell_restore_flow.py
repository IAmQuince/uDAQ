from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper
from universaldaq.common import AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession, ShellViewModelBuilder

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-002', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-ARCH-002', 'UDQ-REQ-UI-006', 'UDQ-REQ-PROF-001'], 'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-STATE-003', 'UDQ-INV-EVID-003'], 'worked_example_reference': None, 'expected_proof_output': 'shell restore workflow'}
pytestmark = pytest.mark.integration


def test_shell_restore_bootstrap_builds_view_model_without_machine_writes():
    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-SHELL'),
        workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=snapshot,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    vm = ShellViewModelBuilder.build(
        workspace_state=boot.session.ui_session.workspace_state,
        authority_surface=boot.session.ui_session.authority_surface,
        graph_session=boot.session.ui_session.graph_session,
    )
    assert boot.session.restore_result.machine_write_intent is False
    assert vm.graph_panel.mode == GraphMode.HISTORY
    assert vm.authority_label == 'review-only'
