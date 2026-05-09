from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    required = ["tests/data/first_slice_requirement_pack.json", "tests/data/first_slice_execution_contract.json", "tests/data/first_slice_invariant_registry.json", "tests/data/first_slice_worked_examples.json"]
    missing = [rel for rel in required if not (root / rel).exists()]
    if missing:
        print("\n".join(missing))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
