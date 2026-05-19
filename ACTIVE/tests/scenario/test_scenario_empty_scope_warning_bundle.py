from __future__ import annotations

import pytest

from universaldaq.common import ActorId, AuthorizationState, ExportArtifactClass, GraphMode, as_event_time
from universaldaq.historian import EvidenceBundleService

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-008', 'verifies_requirements': ['UDQ-REQ-EXP-001', 'UDQ-REQ-HIS-001'], 'checks_invariants': ['UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'empty-scope warning bundle'}
pytestmark = pytest.mark.scenario


def test_empty_scope_export_yields_warning_but_still_builds_manifest():
    service = EvidenceBundleService()
    scope = service.resolve_export_scope(
        graph_mode=GraphMode.REVIEW,
        include_commands=False,
        include_alarms=False,
        include_restores=False,
        include_shell_evidence=False,
    )
    intent = service.build_export_intent(
        export_id='EXPORT-EMPTY-001',
        artifact_class=ExportArtifactClass.EVIDENCE_BUNDLE,
        requested_by_actor=ActorId('reviewer'),
        session_id='SESSION-EMPTY-001',
        requested_at=1,
        authority_state=AuthorizationState.VIEW_ONLY,
        scope=scope,
    )
    result = service.build_bundle_from_intent(
        intent=intent,
        bundle_id='BUNDLE-EMPTY-001',
        manifest_id='MAN-EMPTY-001',
    )

    assert len(result.bundle.records) == 0
    assert any(item.code == 'empty_scope' for item in result.warnings)
    assert result.manifest.omission_notes
    assert any(item.descriptor.relative_path == 'manifest.json' for item in result.serialized_artifacts)
