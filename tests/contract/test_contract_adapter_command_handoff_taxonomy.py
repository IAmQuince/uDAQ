from __future__ import annotations

from universaldaq.adapters import AdapterCommandOutcome, AdapterCommandRequest, SimulatedWritableAdapter
from universaldaq.common import ActorId, OutputId, RequestId, as_event_time

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-ADAPT-002', 'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-MOD-002'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'adapter command handoff outcome matrix'}


def test_adapter_command_handoff_outcomes_distinguish_transport_and_target_failures():
    adapter = SimulatedWritableAdapter(
        adapter_id='SIM-WRITE',
        writable_points={'OUT-1': '0'},
        observed_points={'OUT-1': '0'},
        fail_transport_for={'OUT-1'},
    )
    request = AdapterCommandRequest(
        adapter_id='SIM-WRITE',
        point_id='OUT-1',
        request_id=RequestId('REQ-1'),
        output_id=OutputId('OUT-1'),
        requested_value='1',
        requested_at=as_event_time(1),
        actor_id=ActorId('operator'),
    )
    failed = adapter.submit_command(request)
    missing = adapter.submit_command(
        AdapterCommandRequest(
            adapter_id='SIM-WRITE',
            point_id='OUT-X',
            request_id=RequestId('REQ-2'),
            output_id=OutputId('OUT-X'),
            requested_value='1',
            requested_at=as_event_time(1),
            actor_id=ActorId('operator'),
        )
    )

    assert failed.outcome == AdapterCommandOutcome.TRANSPORT_FAILED
    assert missing.outcome == AdapterCommandOutcome.TARGET_NOT_FOUND
