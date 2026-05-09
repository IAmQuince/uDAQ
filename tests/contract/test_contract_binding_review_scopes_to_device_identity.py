from __future__ import annotations

import pytest

from universaldaq.adapters import AdapterPointRef, PointClass
from universaldaq.common import OutputId, SignalId
from universaldaq.signals import (
    BindingPolicy,
    DevicePointDefinition,
    LogicalOutputBinding,
    LogicalSignalBinding,
    SignalBindingService,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-022',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'binding review scopes counts to the affected device identity',
}
pytestmark = pytest.mark.contract


def test_binding_review_counts_only_bindings_owned_by_target_device_identity():
    service = SignalBindingService()
    service.replace_device_point_definitions(
        device_identity_key='dev-a',
        definitions=(
            DevicePointDefinition(
                point_ref=AdapterPointRef(adapter_id='A1', point_id='analog_in_0', point_class=PointClass.ANALOG),
                device_identity_key='dev-a',
                friendly_name='AIN0',
                role='analog_input',
            ),
        ),
    )
    service.replace_device_point_definitions(
        device_identity_key='dev-b',
        definitions=(
            DevicePointDefinition(
                point_ref=AdapterPointRef(adapter_id='B1', point_id='analog_in_0', point_class=PointClass.ANALOG),
                device_identity_key='dev-b',
                friendly_name='AIN0-B',
                role='analog_input',
            ),
        ),
    )
    service.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('sig-a'),
            source_point_key='A1:analog_in_0',
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
            metadata={'device_identity_key': 'dev-a', 'point_id': 'analog_in_0'},
        )
    )
    service.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('sig-b'),
            source_point_key='B1:analog_in_0',
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
            metadata={'device_identity_key': 'dev-b', 'point_id': 'analog_in_0'},
        )
    )
    service.bind_output(
        LogicalOutputBinding(
            logical_output_id=OutputId('out-b'),
            target_point_key='B1:analog_in_0',
            metadata={'device_identity_key': 'dev-b', 'point_id': 'analog_in_0'},
        )
    )

    summary = service.build_binding_review(device_identity_key='dev-a', auto_apply_rebind=False)

    assert summary.total_signal_binding_count == 1
    assert summary.total_output_binding_count == 0
    assert summary.resolved_signal_count == 1
    assert [item.logical_id for item in summary.items] == ['sig-a']
