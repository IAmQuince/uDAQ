from __future__ import annotations

import pytest

from universaldaq.adapters import AdapterPointRef, PointClass
from universaldaq.app import build_authoritative_binding_inventory, build_default_service_registry
from universaldaq.common import OutputId, SignalId
from universaldaq.signals import (
    BindingPolicy,
    DevicePointDefinition,
    LogicalOutputBinding,
    LogicalSignalBinding,
    SignalDefinition,
)


TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-060',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-SIG-001', 'UDQ-REQ-OUT-002', 'UDQ-REQ-UI-007'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'authoritative binding inventory reflects backend-owned signal and output bindings',
}
pytestmark = pytest.mark.contract


def test_authoritative_binding_inventory_reflects_backend_owned_bindings() -> None:
    services = build_default_service_registry(load_support_packs=False)
    device_identity_key = 'device::alpha'

    source_definition = DevicePointDefinition(
        point_ref=AdapterPointRef(
            adapter_id='SIM-READ-001',
            point_id='PT-101',
            display_name='Pressure In',
            point_class=PointClass.ANALOG,
            units='psi',
        ),
        device_identity_key=device_identity_key,
        friendly_name='Pressure In',
        role='analog_input',
    )
    output_definition = DevicePointDefinition(
        point_ref=AdapterPointRef(
            adapter_id='SIM-WRITE-001',
            point_id='OUT-1',
            display_name='Pump Demand',
            point_class=PointClass.ANALOG,
            units='pct',
        ),
        device_identity_key=device_identity_key,
        friendly_name='Pump Demand',
        role='analog_output',
    )
    services.bindings.register_point_definition(source_definition)
    services.bindings.register_point_definition(output_definition)
    services.signals.register_signal(
        SignalDefinition(signal_id=SignalId('SIG-001'), display_name='pressure_filtered', engineering_units='psi')
    )
    services.bindings.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('SIG-001'),
            source_point_key=source_definition.stable_point_key,
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
            metadata={'device_identity_key': device_identity_key, 'friendly_name': 'Pressure In'},
        )
    )
    services.bindings.bind_output(
        LogicalOutputBinding(
            logical_output_id=OutputId('OUT-001'),
            target_point_key=output_definition.stable_point_key,
            binding_policy=BindingPolicy.MANUAL_REVIEW_REQUIRED,
            metadata={'device_identity_key': device_identity_key, 'friendly_name': 'Pump Demand'},
        )
    )

    inventory = build_authoritative_binding_inventory(
        services=services,
        device_identity_key=device_identity_key,
    )

    assert inventory.total_count == 2
    assert inventory.signal_count == 1
    assert inventory.output_count == 1
    assert {row.authority_kind for row in inventory.rows} == {'backend_applied'}
    assert {row.direction for row in inventory.rows} == {
        'device_input_to_internal_signal',
        'internal_signal_to_device_output',
    }
    assert any(row.logical_display_name == 'pressure_filtered' for row in inventory.rows)


def test_backend_binding_readback_provider_marks_missing_inventory_as_unavailable() -> None:
    services = build_default_service_registry(load_support_packs=False)
    device_identity_key = 'device::missing-point-demo'
    services.signals.register_signal(
        SignalDefinition(signal_id=SignalId('SIG-MISSING'), display_name='missing_source_signal', engineering_units='V')
    )
    services.bindings.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('SIG-MISSING'),
            source_point_key='device::missing-point-demo::AIN999',
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
            metadata={'device_identity_key': device_identity_key, 'friendly_name': 'Missing AIN'},
        )
    )

    from universaldaq.app import BackendBindingReadbackProvider, BindingReadbackStatus

    provider = BackendBindingReadbackProvider(services=services)
    inventory = provider.list_authoritative_bindings(device_identity_key=device_identity_key)

    assert inventory.readback_available is True
    assert inventory.total_count == 1
    assert inventory.degraded_count == 1
    row = inventory.rows[0]
    assert row.authority_kind == 'backend_applied'
    assert row.status == BindingReadbackStatus.UNAVAILABLE.value
    assert row.enabled is False
    assert 'not present' in row.note
