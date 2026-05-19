from __future__ import annotations

import pytest

from universaldaq.adapters import AdapterPointRef, PointClass
from universaldaq.common import SignalId
from universaldaq.signals import (
    BindingPolicy,
    BindingResolutionStatus,
    DevicePointDefinition,
    LogicalSignalBinding,
    SignalBindingService,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-021',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'binding review auto-rebinds to reprojected point inventory for same stable device identity',
}
pytestmark = pytest.mark.contract


def test_binding_review_auto_rebinds_when_same_device_point_is_reprojected_under_new_adapter_key():
    service = SignalBindingService()
    service.replace_device_point_definitions(
        device_identity_key='labjack::u6::111111',
        definitions=(
            DevicePointDefinition(
                point_ref=AdapterPointRef(adapter_id='A1', point_id='analog_in_0', point_class=PointClass.ANALOG),
                device_identity_key='labjack::u6::111111',
                friendly_name='AIN0',
                role='analog_input',
            ),
        ),
    )
    service.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('stack_voltage'),
            source_point_key='A1:analog_in_0',
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
            metadata={'point_id': 'analog_in_0'},
        )
    )

    service.replace_device_point_definitions(
        device_identity_key='labjack::u6::111111',
        definitions=(
            DevicePointDefinition(
                point_ref=AdapterPointRef(adapter_id='A2', point_id='analog_in_0', point_class=PointClass.ANALOG),
                device_identity_key='labjack::u6::111111',
                friendly_name='AIN0 moved',
                role='analog_input',
            ),
        ),
    )

    summary = service.build_binding_review(device_identity_key='labjack::u6::111111', auto_apply_rebind=True)

    rebound = service.resolve_signal_source(SignalId('stack_voltage'))
    assert rebound is not None
    assert rebound.stable_point_key == 'A2:analog_in_0'
    assert summary.auto_rebound_signal_count == 1
    assert summary.items[0].status == BindingResolutionStatus.AUTO_REBOUND
