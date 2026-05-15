from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-028',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'lifecycle review bundle now surfaces checkpoint summary and recovery-tail metadata from the active runtime session',
}
pytestmark = pytest.mark.integration


def test_lifecycle_review_bundle_surfaces_checkpoint_and_recovery_metadata(tmp_path):
    services = build_default_service_registry()
    services.runtime_quality._runtime_root = tmp_path / 'runtime'
    services.runtime_quality.journal.file_path = tmp_path / 'runtime' / 'session.jsonl'
    services.runtime_quality.checkpoints.root_path = tmp_path / 'runtime'

    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-CHECKPOINT'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.services.runtime_quality.record_operational_entry(
        timestamp=as_event_time(3),
        record_type='runtime_event',
        payload={'event_type': 'operator_note', 'message': 'tail row'},
        flush=True,
    )
    controller.services.runtime_quality.write_checkpoint(timestamp=as_event_time(4), payload={'phase': 'review'})

    bundle = controller.lifecycle_review_bundle()
    assert bundle['runtime_checkpoint_summary']['checkpoint_available'] is True
    assert bundle['runtime_checkpoint_summary']['last_committed_sequence_id'] >= 1
    assert bundle['runtime_recovery_bundle']['checkpoint_available'] is True
    assert 'journal_tail' in bundle['runtime_recovery_bundle']
