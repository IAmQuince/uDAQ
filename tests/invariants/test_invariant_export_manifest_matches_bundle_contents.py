from __future__ import annotations

import json

import pytest

from universaldaq.common import ActorId, AuthorizationState, ExportArtifactClass, GraphMode, as_event_time
from universaldaq.historian import EvidenceBundleService
from universaldaq.outputs import CommandTraceFactory, OutputRequest
from universaldaq.common import OutputId, RequestId

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-006', 'verifies_requirements': ['UDQ-REQ-EXP-001', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'manifest matches bundle contents'}
pytestmark = pytest.mark.invariants


def test_manifest_artifacts_match_serialized_bundle_content_counts():
    service = EvidenceBundleService()
    request = OutputRequest(
        request_id=RequestId('REQ-INV-EXP-001'),
        output_id=OutputId('OUT-INV-EXP-001'),
        requested_value='11',
        actor=ActorId('operator'),
        requested_at=as_event_time(1),
    )
    trace = CommandTraceFactory.blocked(request=request, reason='interlock')
    scope = service.resolve_export_scope(graph_mode=GraphMode.REVIEW)
    intent = service.build_export_intent(
        export_id='EXPORT-INV-EXP-001',
        artifact_class=ExportArtifactClass.EVIDENCE_BUNDLE,
        requested_by_actor=ActorId('reviewer'),
        session_id='SESSION-INV-EXP-001',
        requested_at=2,
        authority_state=AuthorizationState.VIEW_ONLY,
        scope=scope,
    )
    result = service.build_bundle_from_intent(
        intent=intent,
        bundle_id='BUNDLE-INV-EXP-001',
        manifest_id='MAN-INV-EXP-001',
        command_traces=(trace,),
    )

    manifest_text = next(item.content for item in result.serialized_artifacts if item.descriptor.relative_path == 'manifest.json')
    manifest_payload = json.loads(manifest_text)
    records_descriptor = next(item for item in manifest_payload['artifacts'] if item['relative_path'] == 'records.csv')
    assert records_descriptor['record_count'] == len(result.bundle.records)
    assert result.bundle.source_counts[0][1] == len(result.bundle.records)
