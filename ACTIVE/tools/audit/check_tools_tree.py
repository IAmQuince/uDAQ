from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    required = ["tools/governance", "tools/traceability", "tools/audit", "tools/diagnostics", "tools/package_build", "tools/proof", "tools/dev"]
    missing = [rel for rel in required if not (root / rel).exists()]
    if missing:
        print("\n".join(missing))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
