from __future__ import annotations

import pytest

from universaldaq.common import ActorId, AlarmId, AlarmLifecycleState, as_event_time
from universaldaq.events import AlarmLifecycle

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-003', 'verifies_requirements': ['UDQ-REQ-EVT-001', 'UDQ-REQ-EVT-002', 'UDQ-REQ-HIS-001'], 'checks_invariants': ['UDQ-INV-TRANS-003', 'UDQ-INV-EVID-002'], 'worked_example_reference': 'UDQ-EXM-004', 'expected_proof_output': 'alarm lifecycle evidence trace'}
pytestmark = pytest.mark.contract


def test_contract_alarm_lifecycle_semantics():
    lifecycle = AlarmLifecycle(alarm_id=AlarmId('ALM-001'))
    lifecycle = lifecycle.assert_alarm(as_event_time(0))
    lifecycle = lifecycle.acknowledge(ActorId('operator'), as_event_time(2))
    lifecycle = lifecycle.return_to_normal(as_event_time(5))
    assert lifecycle.ordered_states == (
        AlarmLifecycleState.ASSERTED,
        AlarmLifecycleState.ACKNOWLEDGED,
        AlarmLifecycleState.RETURNED_TO_NORMAL,
    )
    assert len(lifecycle.evidence_records) == 3
    assert lifecycle.evidence_records[1].attributes['actor'] == 'operator'
