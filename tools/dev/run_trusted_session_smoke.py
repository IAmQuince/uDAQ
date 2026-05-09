from __future__ import annotations

import json

from tools.diagnostics.dump_trusted_session_inventory import build_inventory


def main() -> int:
    payload = build_inventory(sample_count=6, reconnect=True, disconnect_after_polls=3)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
