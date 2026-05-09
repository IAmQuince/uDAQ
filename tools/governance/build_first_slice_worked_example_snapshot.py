from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    path = root / "tests/data/first_slice_worked_examples.json"
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
