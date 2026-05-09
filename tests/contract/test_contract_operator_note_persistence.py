from __future__ import annotations

import pytest

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-056',
    'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-EVID-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'operator notes remain distinct from system evidence and are carried into persisted session summaries',
}
pytestmark = pytest.mark.contract


def test_contract_operator_notes_persist_into_session_summary():
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-NOTES'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    note = controller.add_operator_note(note_text='heater on', timestamp=as_event_time(3), category='operator_annotation')
    summary = controller.build_persisted_session_summary(timestamp=as_event_time(4))
    assert summary.operator_notes[-1].note_id == note.note_id
    assert summary.operator_notes[-1].category == 'operator_annotation'
    assert summary.operator_notes[-1].text == 'heater on'
    assert controller.session_flight_record()['operator_note_count'] == 1
