from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._shared import parse_assignment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    rows = []
    for path in sorted((root / "tests").rglob("test_*.py")):
        rows.append({"path": str(path.relative_to(root)), **parse_assignment(path, "TEST_DECLARATION")})
    out = root / "audit_reports/active/UDQ_TRACEABILITY_SNAPSHOT__2026-03-21_235959.json"
    out.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
