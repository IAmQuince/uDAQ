from __future__ import annotations

import json
import sys
from pathlib import Path


def _serialize_survey(survey) -> dict[str, object]:
    return {
        'summary': survey.summary,
        'support_packs': [
            {
                'pack_id': item.pack_id,
                'state': item.state,
                'summary': item.summary,
            }
            for item in survey.support_packs
        ],
        'devices': [
            {
                'device_key': item.device_key,
                'provider_id': item.provider_id,
                'display_name': item.display_name,
                'support_tier': item.support_tier,
                'transport': item.transport,
                'activation_available': item.activation_available,
                'readable_point_count': item.readable_point_count,
                'writable_point_count': item.writable_point_count,
                'capability_mode': item.capability_mode,
                'identity_state': item.identity_state,
                'read_state': item.read_state,
                'write_state': item.write_state,
                'limited_access_reason': item.limited_access_reason,
                'metadata': dict(item.metadata),
            }
            for item in survey.devices
        ],
    }


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.adapters import survey_runtime_capabilities
    from universaldaq.app import build_default_service_registry
    from universaldaq.common import as_event_time

    generic_services = build_default_service_registry(load_support_packs=False)
    generic_survey = survey_runtime_capabilities(adapters=generic_services.adapters, timestamp=as_event_time(10))

    enhanced_payload: dict[str, object] = {'summary': 'enhanced survey unavailable'}
    try:
        from universaldaq_labjack.models import LabJackProbeRow
        from universaldaq_labjack.plugin import build_support_pack_registration

        enhanced_services = build_default_service_registry(load_support_packs=False)
        enhanced_services.adapters.install_support_pack(
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
        enhanced_survey = survey_runtime_capabilities(adapters=enhanced_services.adapters, timestamp=as_event_time(20))
        enhanced_payload = _serialize_survey(enhanced_survey)
    except Exception as exc:  # pragma: no cover - bounded field fallback
        enhanced_payload = {
            'summary': 'enhanced survey unavailable',
            'error': type(exc).__name__,
            'detail': str(exc),
        }

    payload = {
        'generic': _serialize_survey(generic_survey),
        'enhanced': enhanced_payload,
        'policy_note': 'optional support packs enrich discovery and semantics, but generic baseline discovery remains present without them',
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
