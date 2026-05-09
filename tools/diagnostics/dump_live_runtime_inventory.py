from __future__ import annotations

import json
import sys
from pathlib import Path


PACKAGE_ID = 'UDQ-PKG-20260328-LIVE-RUNTIME-INTEGRATION-AND-SAFE-CONTROL-POSTURE-FOUNDATIONS-R01'


def main() -> int:
    package_root = Path(__file__).resolve().parents[2]
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.ui.live_runtime import LiveRuntimeEngine

    engine = LiveRuntimeEngine()
    payload = {'package_id': PACKAGE_ID, **engine.inventory()}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
