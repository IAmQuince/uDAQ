from __future__ import annotations

import pytest

from universaldaq.common import SignalId, SignalQuality, VariableId, as_event_time
from universaldaq.signals import SignalRegistry, SignalSnapshot, VariableDefinition, VariableEvaluationService, VariableSourceKind, VariableState

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-024',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'connected lineage loss is classified as degraded rather than stale',
}
pytestmark = pytest.mark.contract


def test_variable_without_fallback_becomes_degraded_when_dependency_disconnects():
    registry = SignalRegistry()
    variables = VariableEvaluationService()
    variables.register(
        VariableDefinition(
            variable_id=VariableId('stack_voltage'),
            display_name='Stack Voltage',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId('stack_voltage_signal'),),
        )
    )
    registry.publish_snapshot(
        SignalSnapshot(
            signal_id=SignalId('stack_voltage_signal'),
            value='1.8',
            quality=SignalQuality.GOOD,
            timestamp=as_event_time(1),
        )
    )
    variables.evaluate_all(signal_registry=registry, timestamp=as_event_time(2))

    registry.publish_snapshot(
        SignalSnapshot(
            signal_id=SignalId('stack_voltage_signal'),
            value='1.8',
            quality=SignalQuality.DISCONNECTED,
            timestamp=as_event_time(3),
        )
    )
    result = variables.evaluate_impacted(
        signal_registry=registry,
        timestamp=as_event_time(4),
        changed_signal_ids=(SignalId('stack_voltage_signal'),),
    )

    assert len(result) == 1
    assert result[0].snapshot.state == VariableState.DEGRADED
    assert result[0].snapshot.quality == SignalQuality.DISCONNECTED
