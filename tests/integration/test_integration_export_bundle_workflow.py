from __future__ import annotations

import json

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-005', 'verifies_requirements': ['UDQ-REQ-HIS-001', 'UDQ-REQ-EXP-001', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'end-to-end export bundle workflow'}
pytestmark = pytest.mark.integration


def test_export_bundle_workflow_roundtrips_manifest_and_payloads():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-INT-EXP-001'),
            workspace_state=WorkspaceState(page='review', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.submit_output_request(
        request_id=RequestId('REQ-INT-EXP-001'),
        output_id=OutputId('OUT-INT-EXP-001'),
        requested_value='9',
        actor=ActorId('operator'),
        authorization_state=AuthorizationState.ALLOWED,
        requested_at=as_event_time(3),
        applied_value='9',
        observed_value='9',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-INT-EXP-001'), timestamp=as_event_time(6))
    result = controller.export_evidence_bundle(
        export_id='EXPORT-INT-EXP-001',
        bundle_id='BUNDLE-INT-EXP-001',
        manifest_id='MAN-INT-EXP-001',
        actor=ActorId('auditor'),
        timestamp=as_event_time(7),
        include_profiles=True,
        include_diagnostics=True,
        diagnostics=({'tool': 'integration', 'mode': 'bundle'},),
    )

    manifest_artifact = next(item for item in result.serialized_artifacts if item.descriptor.relative_path == 'manifest.json')
    manifest_payload = json.loads(manifest_artifact.content)
    assert manifest_payload['manifest_id'] == 'MAN-INT-EXP-001'
    assert manifest_payload['artifact_class'] == 'evidence_bundle'
    assert 'profiles.json' in [item.descriptor.relative_path for item in result.serialized_artifacts]
    assert controller.session.last_manifest_id == 'MAN-INT-EXP-001'
