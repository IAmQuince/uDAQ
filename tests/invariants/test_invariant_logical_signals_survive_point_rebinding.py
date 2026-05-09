from __future__ import annotations

import pytest

from universaldaq.adapters import AdapterPointRef
from universaldaq.common import SignalId
from universaldaq.signals import BindingPolicy, DevicePointDefinition, LogicalSignalBinding, SignalBindingService

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-014',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'logical signal remains stable across point rebind proof',
}
pytestmark = pytest.mark.invariants


def test_logical_signal_identifier_remains_stable_when_source_point_changes():
    bindings = SignalBindingService()
    bindings.register_point_definition(
        DevicePointDefinition(
            point_ref=AdapterPointRef(adapter_id='A1', point_id='AIN0'),
            device_identity_key='labjack::u6::111111',
            friendly_name='Voltage Source A',
            role='analog_input',
        )
    )
    bindings.register_point_definition(
        DevicePointDefinition(
            point_ref=AdapterPointRef(adapter_id='A2', point_id='AIN0'),
            device_identity_key='labjack::u6::111111',
            friendly_name='Voltage Source A remapped',
            role='analog_input',
        )
    )
    bindings.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('stack_voltage'),
            source_point_key='A1:AIN0',
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
        )
    )

    rebound = bindings.rebind_signal(logical_signal_id=SignalId('stack_voltage'), replacement_point_key='A2:AIN0')

    assert rebound.logical_signal_id == SignalId('stack_voltage')
    assert bindings.resolve_signal_source(SignalId('stack_voltage')).friendly_name == 'Voltage Source A remapped'
