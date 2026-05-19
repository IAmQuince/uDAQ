from __future__ import annotations

import pytest

from universaldaq.common import ActorId, OutputId, RequestId, as_event_time
from universaldaq.outputs import CommandTraceFactory, OutputRequest

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-001', 'verifies_requirements': ['UDQ-REQ-OUT-001', 'UDQ-REQ-OUT-002'], 'checks_invariants': ['UDQ-INV-TRANS-001', 'UDQ-INV-EVID-001'], 'worked_example_reference': 'UDQ-EXM-001', 'expected_proof_output': 'command-path invariant report'}
pytestmark = pytest.mark.invariants


def test_invariant_command_path():
    request = OutputRequest(
        request_id=RequestId('REQ-INV-001'),
        output_id=OutputId('OUT-INV-001'),
        requested_value='on',
        actor=ActorId('operator'),
        requested_at=as_event_time(0),
    )
    trace = CommandTraceFactory.blocked(request=request, reason='interlock')
    assert trace.apply_published is False
    assert all('request_id' in record.attributes or 'reason' in record.attributes for record in trace.evidence_records)
