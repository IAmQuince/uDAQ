from __future__ import annotations

import json

from tools.diagnostics.dump_first_signal_inventory import build_inventory


def main() -> int:
    payload = build_inventory(sample_count=6)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
