from __future__ import annotations

import pytest

from universaldaq.common import SignalId, SignalQuality, VariableId, as_event_time
from universaldaq.signals import SignalRegistry, SignalSnapshot, VariableDefinition, VariableEvaluationService, VariableSourceKind

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-023',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'impacted-variable evaluation touches only the affected dependency closure',
}
pytestmark = pytest.mark.contract


def test_impacted_variable_evaluation_updates_only_dependency_closure():
    registry = SignalRegistry()
    registry.publish_snapshot(SignalSnapshot(signal_id=SignalId('s1'), value='10', quality=SignalQuality.GOOD, timestamp=as_event_time(1)))
    registry.publish_snapshot(SignalSnapshot(signal_id=SignalId('s2'), value='5', quality=SignalQuality.GOOD, timestamp=as_event_time(1)))
    variables = VariableEvaluationService()
    variables.register(
        VariableDefinition(
            variable_id=VariableId('va'),
            display_name='A',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId('s1'),),
        )
    )
    variables.register(
        VariableDefinition(
            variable_id=VariableId('vb'),
            display_name='B',
            source_kind=VariableSourceKind.EXPRESSION,
            expression='va + 1',
            variable_dependencies=(VariableId('va'),),
            dependency_aliases={'va': 'va'},
        )
    )
    variables.register(
        VariableDefinition(
            variable_id=VariableId('vc'),
            display_name='C',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId('s2'),),
        )
    )
    variables.evaluate_all(signal_registry=registry, timestamp=as_event_time(2))
    original_c_timestamp = variables.snapshots[VariableId('vc')].timestamp

    registry.publish_snapshot(SignalSnapshot(signal_id=SignalId('s1'), value='12', quality=SignalQuality.GOOD, timestamp=as_event_time(3)))
    results = variables.evaluate_impacted(
        signal_registry=registry,
        timestamp=as_event_time(4),
        changed_signal_ids=(SignalId('s1'),),
    )

    assert {result.snapshot.variable_id for result in results} == {VariableId('va'), VariableId('vb')}
    assert variables.snapshots[VariableId('va')].value == '12'
    assert variables.snapshots[VariableId('vb')].value == '13'
    assert variables.snapshots[VariableId('vc')].timestamp == original_c_timestamp
