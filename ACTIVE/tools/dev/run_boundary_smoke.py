from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.adapters import survey_runtime_capabilities
    from universaldaq.app import build_default_service_registry
    from universaldaq.common import as_event_time
    from universaldaq.ui.live_runtime import LiveRuntimeEngine

    services = build_default_service_registry(load_support_packs=False)
    survey = survey_runtime_capabilities(adapters=services.adapters, timestamp=as_event_time(10))
    engine = LiveRuntimeEngine(load_support_packs=False)
    devices = engine.available_devices()
    connected = False
    write_outcome = 'not_attempted'
    if devices:
        connected = engine.connect(device_key=devices[0].device_key)
        if connected:
            engine.step()
            write_outcome = engine.request_write(point_id='analog_out_0', request_value='1.250', posture='armed_control').result.outcome.value
    payload = {
        'generic_survey_summary': survey.summary,
        'generic_device_count': len(survey.devices),
        'support_pack_count': len(survey.support_packs),
        'live_runtime_device_count': len(devices),
        'connected': connected,
        'write_outcome': write_outcome,
    }
    print('boundary-smoke: ' + json.dumps(payload, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
