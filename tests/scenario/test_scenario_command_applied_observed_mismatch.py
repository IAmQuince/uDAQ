from __future__ import annotations

import json

import pytest

from tests.conftest import DATA_ROOT
from universaldaq.common import ActorId, OutputId, RequestId, as_event_time
from universaldaq.outputs import CommandTraceFactory, OutputRequest

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-002', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-OUT-002', 'UDQ-REQ-EVT-001'], 'checks_invariants': ['UDQ-INV-TIME-002', 'UDQ-INV-EVID-001'], 'worked_example_reference': 'UDQ-EXM-002', 'expected_proof_output': 'mismatch proof bundle'}
pytestmark = pytest.mark.scenario


def test_scenario_command_applied_observed_mismatch():
    sample = json.loads((DATA_ROOT / 'sample_applied_observed_mismatch_trace.json').read_text(encoding='utf-8'))['trace']
    request = OutputRequest(
        request_id=RequestId('REQ-101'),
        output_id=OutputId('OUT-101'),
        requested_value='on',
        actor=ActorId('operator'),
        requested_at=as_event_time(sample[0]['t']),
    )
    trace = CommandTraceFactory.applied_then_observed(
        request=request,
        applied_value=sample[1]['state'],
        observed_value=sample[2]['observed'],
        applied_at=as_event_time(sample[1]['t']),
        observed_at=as_event_time(sample[2]['t']),
    )
    assert trace.apply_published is True
    assert trace.observed_mismatch is True
    assert trace.comparison is not None and trace.comparison.compared_at == 5
    assert trace.evidence_records[-1].attributes['expected_value'] == 'on'
