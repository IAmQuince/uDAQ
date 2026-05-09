from __future__ import annotations

import pytest

from universaldaq.adapters import AdapterManagerService
from universaldaq.adapters.simulated import SimulatedWritableAdapter
from universaldaq.common import ActorId, OutputId, RequestId, as_event_time
from universaldaq.outputs import (
    CommandArbitrationBroker,
    OutputCommandService,
    SafeStatePolicy,
    WritableTagBinding,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-047',
    'verifies_requirements': ['UDQ-REQ-OUT-001', 'UDQ-REQ-OUT-002', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'bounded command arbitration rejects ownership conflicts, expires stale leases, and rejects unavailable targets without vendor-specific core logic',
}
pytestmark = pytest.mark.contract


def _build_broker() -> CommandArbitrationBroker:
    manager = AdapterManagerService()
    manager.register(
        SimulatedWritableAdapter(
            adapter_id='device_alpha_001',
            writable_points={'digital_out_0': '0'},
            observed_points={'digital_out_0': '0'},
        )
    )
    broker = CommandArbitrationBroker(adapter_manager=manager, output_service=OutputCommandService())
    broker.register_binding(
        WritableTagBinding(
            output_id=OutputId('device_alpha_001:digital_out_0'),
            tag_key='device_alpha_001:digital_out_0',
            adapter_id='device_alpha_001',
            point_id='digital_out_0',
            display_name='digital_out_0',
            safe_state_policy=SafeStatePolicy.RETURN_TO_SAFE,
            safe_state_value='0',
        )
    )
    return broker


def test_command_arbitration_rejects_conflict_then_allows_after_lease_expiry():
    broker = _build_broker()

    first = broker.issue_command(
        request_id=RequestId('REQ-CMD-001'),
        output_id=OutputId('device_alpha_001:digital_out_0'),
        requested_value='1',
        actor=ActorId('manual'),
        requested_at=as_event_time(10),
        lease_duration_ticks=2,
    )
    assert first.disposition == 'accepted'
    assert first.successful is True

    conflict = broker.issue_command(
        request_id=RequestId('REQ-CMD-002'),
        output_id=OutputId('device_alpha_001:digital_out_0'),
        requested_value='0',
        actor=ActorId('runtime'),
        requested_at=as_event_time(11),
        lease_duration_ticks=2,
    )
    assert conflict.disposition == 'ownership_conflict'
    assert conflict.trace.rejection_phase == 'arbitration'

    after_expiry = broker.issue_command(
        request_id=RequestId('REQ-CMD-003'),
        output_id=OutputId('device_alpha_001:digital_out_0'),
        requested_value='0',
        actor=ActorId('runtime'),
        requested_at=as_event_time(13),
        lease_duration_ticks=2,
    )
    assert after_expiry.disposition == 'accepted'
    assert any(event.event_type == 'lease_expired' for event in broker.events)


def test_command_arbitration_rejects_unavailable_target_and_emits_safe_state_requirement():
    broker = _build_broker()

    events = broker.set_output_availability(
        output_id=OutputId('device_alpha_001:digital_out_0'),
        available=False,
        timestamp=as_event_time(20),
        summary='bounded degradation test',
    )
    assert any(event.event_type == 'target_degraded' for event in events)
    assert any(event.event_type == 'safe_state_required' for event in events)

    result = broker.issue_command(
        request_id=RequestId('REQ-CMD-004'),
        output_id=OutputId('device_alpha_001:digital_out_0'),
        requested_value='1',
        actor=ActorId('manual'),
        requested_at=as_event_time(21),
        lease_duration_ticks=2,
    )
    assert result.disposition == 'target_unavailable'
    assert result.trace.rejection_phase == 'arbitration'


def test_same_owner_command_renews_lease_and_degrade_revokes_it():
    broker = _build_broker()

    first = broker.issue_command(
        request_id=RequestId('REQ-CMD-010'),
        output_id=OutputId('device_alpha_001:digital_out_0'),
        requested_value='1',
        actor=ActorId('manual'),
        requested_at=as_event_time(30),
        lease_duration_ticks=3,
    )
    assert first.disposition == 'accepted'

    renewed = broker.issue_command(
        request_id=RequestId('REQ-CMD-011'),
        output_id=OutputId('device_alpha_001:digital_out_0'),
        requested_value='0',
        actor=ActorId('manual'),
        requested_at=as_event_time(31),
        lease_duration_ticks=4,
    )
    assert renewed.disposition == 'accepted'
    assert any(event.event_type == 'ownership_renewed' for event in renewed.broker_events)
    active = broker.active_leases(timestamp=as_event_time(31))
    assert len(active) == 1
    assert int(active[0].expires_at) == 35

    events = broker.set_output_availability(
        output_id=OutputId('device_alpha_001:digital_out_0'),
        available=False,
        timestamp=as_event_time(32),
        summary='simulated degrade clears lease',
    )
    assert any(event.event_type == 'lease_revoked_on_degrade' for event in events)
    assert broker.active_leases(timestamp=as_event_time(32)) == ()

    rejected = broker.issue_command(
        request_id=RequestId('REQ-CMD-012'),
        output_id=OutputId('device_alpha_001:digital_out_0'),
        requested_value='1',
        actor=ActorId('manual'),
        requested_at=as_event_time(33),
        lease_duration_ticks=2,
    )
    assert rejected.disposition == 'target_unavailable'
