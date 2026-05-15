from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))
    from universaldaq.app import build_default_service_registry

    services = build_default_service_registry()
    payload = {
        'signals_service': type(services.signals).__name__,
        'outputs_service': type(services.outputs).__name__,
        'events_service': type(services.events).__name__,
        'profiles_service': type(services.profiles).__name__,
        'historian_service': type(services.historian).__name__,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
