from __future__ import annotations

import pytest

from universaldaq.common import ActorId, ExportArtifactClass
from universaldaq.security import ActorContext, AuthorizationService, RoleClass

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-016', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'artifact-class export permissions'}
pytestmark = pytest.mark.contract


def test_export_permission_varies_by_artifact_class_for_observer_role():
    service = AuthorizationService.from_default_policy()
    actor = ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER, session_id='SESSION-EXP')
    review = service.can_export_artifact(actor_context=actor, artifact_class=ExportArtifactClass.REVIEW_ARTIFACT)
    bundle = service.can_export_artifact(actor_context=actor, artifact_class=ExportArtifactClass.EVIDENCE_BUNDLE)
    assert review.allowed is True
    assert bundle.allowed is False
