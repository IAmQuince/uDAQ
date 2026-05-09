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
    try:
        from universaldaq_labjack.models import LabJackProbeRow
        from universaldaq_labjack.plugin import build_support_pack_registration

        services.adapters.install_support_pack(
            build_support_pack_registration(
                probe_rows=(
                    LabJackProbeRow(
                        model='U6',
                        serial_number='470001',
                        transport='usb',
                        firmware_version='1.00',
                        hardware_revision='A',
                        connection_label='bench-u6',
                    ),
                )
            )
        )
    except Exception:
        pass

    discovered = services.adapters.discover_devices(timestamp=as_event_time(20))
    activated = None
    if discovered:
        device, adapter_id, workbenches = services.adapters.activate_discovered_device(device_key=discovered[0].device_key)
        activated = {
            'device_key': device.device_key,
            'adapter_id': adapter_id,
            'workbenches': [item.display_name for item in workbenches],
        }
    payload = {
        'support_pack_ids': list(sorted(services.adapters.support_packs.keys())),
        'provider_ids': list(sorted(services.adapters.discovery_providers.keys())),
        'discovered_devices': [
            {
                'device_key': device.device_key,
                'display_name': device.display_name,
                'support_tier': device.support_tier.value,
                'capability_labels': list(device.capability_labels),
                'serial_number': device.identity.serial_number,
                'transport': device.identity.transport,
                'known_device_key': device.known_device_key,
            }
            for device in discovered
        ],
        'activated': activated,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
