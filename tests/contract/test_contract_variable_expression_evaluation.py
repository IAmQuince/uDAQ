from __future__ import annotations

import pytest

from universaldaq.common import SignalId, SignalQuality, VariableId, as_event_time
from universaldaq.signals import (
    SignalRegistry,
    SignalSnapshot,
    VariableDefinition,
    VariableEvaluationService,
    VariableSourceKind,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-021',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'variable evaluation contract proof',
}
pytestmark = pytest.mark.contract


def test_expression_variable_can_depend_on_signal_and_variable_values():
    registry = SignalRegistry()
    registry.publish_snapshot(
        SignalSnapshot(
            signal_id=SignalId('cell_temp'),
            value='72',
            quality=SignalQuality.GOOD,
            timestamp=as_event_time(1),
        )
    )
    variables = VariableEvaluationService()
    variables.register(
        VariableDefinition(
            variable_id=VariableId('setpoint'),
            display_name='Temperature Setpoint',
            source_kind=VariableSourceKind.CONSTANT,
            constant_value='80',
            engineering_units='degF',
        )
    )
    variables.register(
        VariableDefinition(
            variable_id=VariableId('temp_error'),
            display_name='Temperature Error',
            source_kind=VariableSourceKind.EXPRESSION,
            expression='setpoint - cell_temp',
            signal_dependencies=(SignalId('cell_temp'),),
            variable_dependencies=(VariableId('setpoint'),),
            dependency_aliases={'cell_temp': 'cell_temp', 'setpoint': 'setpoint'},
            engineering_units='degF',
        )
    )

    constant = variables.evaluate(VariableId('setpoint'), signal_registry=registry, timestamp=as_event_time(2))
    result = variables.evaluate(
        VariableId('temp_error'),
        signal_registry=registry,
        timestamp=as_event_time(3),
        variable_snapshots={VariableId('setpoint'): constant.snapshot},
    )

    assert constant.snapshot.value == '80'
    assert result.snapshot.value == '8'
    assert result.snapshot.quality == SignalQuality.GOOD
    assert result.resolved_dependencies == {'cell_temp': '72', 'setpoint': '80'}
