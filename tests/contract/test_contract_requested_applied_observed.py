from __future__ import annotations

import pytest

from universaldaq.common import ActorId, OutputId, RequestId, as_event_time
from universaldaq.outputs import CommandTraceFactory, OutputRequest, validate_command_trace

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-001', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-OUT-001', 'UDQ-REQ-OUT-002'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-TRANS-001', 'UDQ-INV-TIME-002'], 'worked_example_reference': 'UDQ-EXM-001', 'expected_proof_output': 'requested/applied/observed trace'}
pytestmark = pytest.mark.contract


def test_contract_requested_applied_observed():
    request = OutputRequest(
        request_id=RequestId('REQ-001'),
        output_id=OutputId('OUT-001'),
        requested_value='on',
        actor=ActorId('operator'),
        requested_at=as_event_time(0),
    )
    trace = CommandTraceFactory.applied_then_observed(
        request=request,
        applied_value='on',
        observed_value='off',
        applied_at=as_event_time(1),
        observed_at=as_event_time(5),
    )
    report = validate_command_trace(trace)
    assert report.ok
    assert trace.request.requested_value == 'on'
    assert trace.applied_state is not None and trace.applied_state.applied_value == 'on'
    assert trace.observed_state is not None and trace.observed_state.observed_value == 'off'
    assert trace.comparison is not None and trace.comparison.is_match is False
    assert trace.observed_mismatch is True
