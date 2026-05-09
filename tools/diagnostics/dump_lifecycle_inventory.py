from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.adapters import AdapterPointRef, DeviceIdentity
    from universaldaq.app import build_default_service_registry
    from universaldaq.common import SignalId, SignalQuality, VariableId, as_event_time
    from universaldaq.signals import (
        BindingPolicy,
        DevicePointDefinition,
        LogicalSignalBinding,
        SignalDefinition,
        SignalSnapshot,
        VariableDefinition,
        VariableSourceKind,
    )

    services = build_default_service_registry()
    timestamp = as_event_time(50)

    exact = services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='labjack::u6::470001',
            display_name='LabJack U6',
            vendor='LabJack',
            model='U6',
            serial_number='470001',
            transport='usb',
        ),
        provider_id='labjack_bridge',
        transport_path='usb:1',
        timestamp=timestamp,
    )
    ambiguous = services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='generic::arduino::candidate-a',
            display_name='Arduino Candidate',
            vendor='Arduino',
            model='Uno',
            transport='usb',
            provisional=True,
        ),
        provider_id='generic_probe',
        transport_path='usb:9',
        timestamp=as_event_time(51),
    )
    services.signals.register_signal(
        SignalDefinition(signal_id=SignalId('stack_pressure'), display_name='Stack Pressure', engineering_units='psi')
    )
    services.signals.publish_snapshot(
        SignalSnapshot(signal_id=SignalId('stack_pressure'), value='100.0', quality=SignalQuality.GOOD, timestamp=as_event_time(52))
    )
    services.bindings.register_point_definition(
        DevicePointDefinition(
            point_ref=AdapterPointRef(adapter_id='SIM-READ-001', point_id='PT-101', display_name='PT-101'),
            device_identity_key=exact.device_record.stable_identity_key,
            friendly_name='Stack Pressure Sensor',
            role='analog_input',
        )
    )
    services.bindings.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('stack_pressure'),
            source_point_key='SIM-READ-001:PT-101',
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
        )
    )
    services.variables.register(
        VariableDefinition(
            variable_id=VariableId('pressure_trip'),
            display_name='Pressure Trip',
            source_kind=VariableSourceKind.EXPRESSION,
            expression='stack_pressure > 95',
            signal_dependencies=(SignalId('stack_pressure'),),
            dependency_aliases={'stack_pressure': 'stack_pressure'},
        )
    )
    services.variables.evaluate(VariableId('pressure_trip'), signal_registry=services.signals, timestamp=as_event_time(53))

    payload = {
        'device_records': [
            {
                'device_record_id': record.device_record_id,
                'stable_identity_key': record.stable_identity_key,
                'display_name': record.display_name,
                'serial_number': record.serial_number,
                'current_connection_instance_id': record.current_connection_instance_id,
                'last_transport_path': record.last_transport_path,
            }
            for record in sorted(services.device_registry.device_records.values(), key=lambda item: item.device_record_id)
        ],
        'connections': [
            {
                'connection_instance_id': connection.connection_instance_id,
                'device_record_id': connection.device_record_id,
                'state': connection.state.value,
                'transport_path': connection.transport_path,
            }
            for connection in sorted(services.device_registry.connections.values(), key=lambda item: item.connection_instance_id)
        ],
        'reconciliation_outcomes': {
            'exact': exact.kind.value,
            'ambiguous': ambiguous.kind.value,
        },
        'signal_bindings': [
            {
                'logical_signal_id': str(signal_id),
                'source_point_key': binding.source_point_key,
                'binding_policy': binding.binding_policy.value,
            }
            for signal_id, binding in sorted(services.bindings.signal_bindings.items(), key=lambda item: str(item[0]))
        ],
        'variable_definitions': [
            {
                'variable_id': str(variable_id),
                'display_name': definition.display_name,
                'source_kind': definition.source_kind.value,
                'expression': definition.expression,
            }
            for variable_id, definition in sorted(services.variables.definitions.items(), key=lambda item: str(item[0]))
        ],
        'object_counts': {
            'device_record_count': len(services.device_registry.device_records),
            'connection_count': len(services.device_registry.connections),
            'point_definition_count': len(services.bindings.point_definitions),
            'signal_binding_count': len(services.bindings.signal_bindings),
            'variable_definition_count': len(services.variables.definitions),
            'variable_snapshot_count': len(services.variables.snapshots),
        },
        'runtime_performance': services.runtime_metrics.snapshot(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
