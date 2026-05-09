from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    report = root / "audit_reports/active/UDQ_STRUCTURE_REPORT__2026-03-21_235959.md"
    lines = ["# Structure Report", "", "## Top-level directories"]
    for path in sorted(p.name for p in root.iterdir() if p.is_dir()):
        lines.append(f"- {path}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
