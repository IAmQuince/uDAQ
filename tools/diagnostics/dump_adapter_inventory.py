from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.app import build_default_service_registry
    from universaldaq.common import as_event_time

    services = build_default_service_registry()
    discovered = services.adapters.discover_devices(timestamp=as_event_time(9))
    poll_results = services.adapters.poll_all(timestamp=as_event_time(10))
    payload = {
        'adapter_ids': list(services.adapters.adapter_ids()),
        'support_packs': [
            {
                'pack_id': registration.descriptor.pack_id,
                'display_name': registration.descriptor.display_name,
                'enhancement_only': registration.descriptor.enhancement_only,
                'provides_driver_bridge': registration.descriptor.provides_driver_bridge,
            }
            for registration in services.adapters.support_packs.values()
        ],
        'discovery_providers': list(sorted(services.adapters.discovery_providers.keys())),
        'discovered_devices': [
            {
                'device_key': device.device_key,
                'display_name': device.display_name,
                'support_tier': device.support_tier.value,
                'transport': device.identity.transport,
                'known_device_key': device.known_device_key,
                'bound_adapter_id': device.bound_adapter_id,
                'workbenches': [item.display_name for item in device.workbenches],
            }
            for device in discovered
        ],
        'capabilities': [
            {
                'adapter_id': capability.adapter_id,
                'kind': capability.adapter_kind.value,
                'mode': capability.operation_mode.value,
                'readable_points': [point.point_id for point in capability.readable_points],
                'writable_points': [point.point_id for point in capability.writable_points],
                'is_simulated': capability.is_simulated,
                'metadata': dict(capability.metadata),
            }
            for capability in services.adapters.capability_inventory()
        ],
        'health': [
            {
                'adapter_id': health.adapter_id,
                'state': health.state.value,
                'summary': health.summary,
            }
            for health in services.adapters.health_inventory()
        ],
        'poll_results': [
            {
                'adapter_id': result.adapter_id,
                'snapshot_count': len(result.snapshots),
                'diagnostics': list(result.diagnostics),
            }
            for result in poll_results
        ],
        'snapshot_rows': [snapshot.export_row() for snapshot in services.adapters.snapshots()],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
