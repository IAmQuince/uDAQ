from __future__ import annotations

import pytest

from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, RequestId, as_event_time
from universaldaq.events import AlarmLifecycleService
from universaldaq.historian import EvidenceBundleService, summarize_bundle
from universaldaq.outputs import OutputArbiter, OutputCommandService

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-003', 'verifies_requirements': ['UDQ-REQ-OUT-001', 'UDQ-REQ-EVT-001', 'UDQ-REQ-HIS-001', 'UDQ-REQ-EXP-001'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-TRANS-003', 'UDQ-INV-EVID-002', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'evidence bundle workflow'}
pytestmark = pytest.mark.integration


def test_command_alarm_and_bundle_workflow():
    outputs = OutputCommandService()
    request = OutputArbiter.build_request(
        request_id=RequestId('REQ-INT-001'),
        output_id=OutputId('OUT-001'),
        requested_value='1',
        actor=ActorId('operator'),
        requested_at=as_event_time(10),
    )
    trace = outputs.submit(
        request=request,
        authorization_state=AuthorizationState.ALLOWED,
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(11),
        observed_at=as_event_time(12),
    )
    alarms = AlarmLifecycleService()
    lifecycle = alarms.assert_alarm(AlarmId('ALM-001'), as_event_time(20))
    lifecycle = alarms.acknowledge(AlarmId('ALM-001'), ActorId('operator'), as_event_time(21))
    bundle_service = EvidenceBundleService()
    bundle = bundle_service.build_bundle(
        bundle_id='BUNDLE-001',
        review_mode=GraphMode.REVIEW,
        command_traces=(trace,),
        alarm_lifecycles=(lifecycle,),
        overlays=('trace-overlay',),
    )
    summary = summarize_bundle(bundle)
    assert summary.record_count == len(trace.evidence_records) + len(lifecycle.evidence_records)
    assert summary.overlay_count == 1
    assert summary.review_mode == 'review'
