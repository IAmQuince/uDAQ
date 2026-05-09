from __future__ import annotations

import pytest

from universaldaq.common import SignalId, SignalQuality, VariableId, as_event_time
from universaldaq.signals import SignalRegistry, SignalSnapshot, VariableDefinition, VariableEvaluationService, VariableSourceKind

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-024',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-SEC-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'bounded expression evaluator safeguards',
}
pytestmark = pytest.mark.contract


def _registry_with_signal() -> SignalRegistry:
    registry = SignalRegistry()
    registry.publish_snapshot(
        SignalSnapshot(
            signal_id=SignalId('sensor'),
            value='2',
            quality=SignalQuality.GOOD,
            timestamp=as_event_time(1),
        )
    )
    return registry


def test_expression_length_limit_yields_invalid_snapshot():
    variables = VariableEvaluationService()
    variables.register(
        VariableDefinition(
            variable_id=VariableId('too_long'),
            display_name='Too Long',
            source_kind=VariableSourceKind.EXPRESSION,
            expression='1+' * 130 + '1',
        )
    )

    result = variables.evaluate(VariableId('too_long'), signal_registry=_registry_with_signal(), timestamp=as_event_time(2))

    assert result.snapshot.state.value == 'invalid'
    assert result.snapshot.quality == SignalQuality.INVALID


def test_large_power_exponent_is_rejected():
    variables = VariableEvaluationService()
    variables.register(
        VariableDefinition(
            variable_id=VariableId('pow_limit'),
            display_name='Pow Limit',
            source_kind=VariableSourceKind.EXPRESSION,
            expression='sensor ** 99',
            signal_dependencies=(SignalId('sensor'),),
            dependency_aliases={'sensor': 'sensor'},
        )
    )

    result = variables.evaluate(VariableId('pow_limit'), signal_registry=_registry_with_signal(), timestamp=as_event_time(2))

    assert result.snapshot.state.value == 'invalid'
    assert result.snapshot.quality == SignalQuality.INVALID


def test_deeply_nested_expression_is_rejected():
    nested = 'sensor'
    for _ in range(80):
        nested = f'({nested}+1)'
    variables = VariableEvaluationService()
    variables.register(
        VariableDefinition(
            variable_id=VariableId('nested_limit'),
            display_name='Nested Limit',
            source_kind=VariableSourceKind.EXPRESSION,
            expression=nested,
            signal_dependencies=(SignalId('sensor'),),
            dependency_aliases={'sensor': 'sensor'},
        )
    )

    result = variables.evaluate(VariableId('nested_limit'), signal_registry=_registry_with_signal(), timestamp=as_event_time(2))

    assert result.snapshot.state.value == 'invalid'
    assert result.snapshot.quality == SignalQuality.INVALID
