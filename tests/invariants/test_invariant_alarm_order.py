from __future__ import annotations

import pytest

from universaldaq.common import ActorId, AlarmId, AlarmLifecycleState, as_event_time
from universaldaq.events import AlarmLifecycle

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-003', 'verifies_requirements': ['UDQ-REQ-EVT-001', 'UDQ-REQ-EVT-002'], 'checks_invariants': ['UDQ-INV-TRANS-003', 'UDQ-INV-EVID-002'], 'worked_example_reference': 'UDQ-EXM-004', 'expected_proof_output': 'alarm-order invariant report'}
pytestmark = pytest.mark.invariants


def test_invariant_alarm_order():
    lifecycle = AlarmLifecycle(alarm_id=AlarmId('ALM-INV-001'))
    lifecycle = lifecycle.assert_alarm(as_event_time(0)).acknowledge(ActorId('operator'), as_event_time(1)).return_to_normal(as_event_time(2))
    assert lifecycle.ordered_states[0] == AlarmLifecycleState.ASSERTED
    assert lifecycle.ordered_states[-1] == AlarmLifecycleState.RETURNED_TO_NORMAL
    assert lifecycle.transitions[1].actor == ActorId('operator')
