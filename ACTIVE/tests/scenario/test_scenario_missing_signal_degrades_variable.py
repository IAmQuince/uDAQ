from __future__ import annotations

import pytest

from universaldaq.common import SignalId, SignalQuality, VariableId, as_event_time
from universaldaq.signals import SignalRegistry, VariableDefinition, VariableEvaluationService, VariableSourceKind, VariableState

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SCN-018',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'missing-signal degradation proof',
}
pytestmark = pytest.mark.scenario


def test_missing_signal_causes_variable_to_use_fallback_and_mark_substituted():
    registry = SignalRegistry()
    variables = VariableEvaluationService()
    variables.register(
        VariableDefinition(
            variable_id=VariableId('pressure_trip'),
            display_name='Pressure Trip',
            source_kind=VariableSourceKind.EXPRESSION,
            expression='stack_pressure > 95',
            signal_dependencies=(SignalId('stack_pressure'),),
            dependency_aliases={'stack_pressure': 'stack_pressure'},
            fallback_value='False',
        )
    )

    result = variables.evaluate(VariableId('pressure_trip'), signal_registry=registry, timestamp=as_event_time(40))

    assert result.snapshot.state == VariableState.SUBSTITUTED
    assert result.snapshot.quality == SignalQuality.STALE
    assert result.snapshot.value == 'False'
    assert result.missing_dependencies == ('stack_pressure',)
