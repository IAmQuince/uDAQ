from universaldaq.common import AlarmId, SignalQuality, VariableId, as_event_time
from universaldaq.events import AlarmDefinition, AlarmLifecycleService
from universaldaq.signals import VariableSnapshot, VariableState

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-014',
    'verifies_requirements': ['UDQ-REQ-EVT-001', 'UDQ-REQ-EVT-002'],
    'checks_invariants': ['UDQ-INV-TRANS-003'],
    'worked_example_reference': 'UDQ-EXM-011',
    'expected_proof_output': 'transition-based alarm raises once, does not spam on repeated active cycles, and clears on recovery',
}


def _snapshot(*, value: str, quality: SignalQuality, state: VariableState, timestamp: int) -> VariableSnapshot:
    return VariableSnapshot(
        variable_id=VariableId('avg_abc'),
        value=value,
        quality=quality,
        state=state,
        timestamp=as_event_time(timestamp),
        dependency_values={'a': value},
    )


def test_contract_events_alarm_spine_raises_once_and_clears_on_recovery():
    service = AlarmLifecycleService()
    service.register_alarm_definition(
        AlarmDefinition(
            alarm_id=AlarmId('ALM-CON-DEGRADED'),
            summary='Average input degraded',
            severity='warning',
            source_kind='variable',
            source_id='avg_abc',
            variable_id=VariableId('avg_abc'),
            condition_kind='variable_state',
            trigger_states=(VariableState.DEGRADED,),
            trigger_qualities=(SignalQuality.DISCONNECTED,),
        )
    )

    first = service.evaluate_variable_snapshots(
        timestamp=as_event_time(10),
        snapshots={VariableId('avg_abc'): _snapshot(value='0.3', quality=SignalQuality.DISCONNECTED, state=VariableState.DEGRADED, timestamp=10)},
    )
    second = service.evaluate_variable_snapshots(
        timestamp=as_event_time(11),
        snapshots={VariableId('avg_abc'): _snapshot(value='0.3', quality=SignalQuality.DISCONNECTED, state=VariableState.DEGRADED, timestamp=11)},
    )
    recovered = service.evaluate_variable_snapshots(
        timestamp=as_event_time(12),
        snapshots={VariableId('avg_abc'): _snapshot(value='0.4', quality=SignalQuality.GOOD, state=VariableState.HEALTHY, timestamp=12)},
    )

    assert [event.event_type for event in first.events] == ['alarm_raised']
    assert second.events == ()
    assert [event.event_type for event in recovered.events] == ['alarm_cleared']
    assert [state.value for state in service.lifecycles[AlarmId('ALM-CON-DEGRADED')].ordered_states] == ['asserted', 'returned_to_normal']
    assert service.summary()['active_alarm_count'] == 0
