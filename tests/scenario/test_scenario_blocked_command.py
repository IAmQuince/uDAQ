from __future__ import annotations

import json

import pytest

from tests.conftest import DATA_ROOT
from universaldaq.common import ActorId, OutputId, RequestId, as_event_time
from universaldaq.outputs import CommandTraceFactory, OutputRequest

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-001', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-OUT-001', 'UDQ-REQ-SEC-001'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-TRANS-001', 'UDQ-INV-EVID-001'], 'worked_example_reference': 'UDQ-EXM-001', 'expected_proof_output': 'blocked command proof bundle'}
pytestmark = pytest.mark.scenario


def test_scenario_blocked_command():
    sample = json.loads((DATA_ROOT / 'sample_blocked_command_trace.json').read_text(encoding='utf-8'))['trace']
    request = OutputRequest(
        request_id=RequestId('REQ-100'),
        output_id=OutputId('OUT-100'),
        requested_value='on',
        actor=ActorId('operator'),
        requested_at=as_event_time(sample[0]['t']),
    )
    trace = CommandTraceFactory.blocked(request=request, reason='interlock')
    assert [event['event'] for event in sample] == ['request_issued', 'authorization_checked', 'arbitration_result', 'rejection_recorded']
    assert trace.decision.value == 'blocked'
    assert trace.apply_published is False
    assert trace.rejection_reason == 'interlock'
    assert trace.evidence_records[-1].attributes['apply_published'] == 'false'
