from __future__ import annotations

import argparse
from pathlib import Path

from tools._shared import load_json, parse_assignment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    valid = {row["worked_example_id"] for row in load_json(root / "tests/data/first_slice_worked_examples.json")["examples"]}
    failures = []
    for path in sorted((root / "tests").rglob("test_*.py")):
        decl = parse_assignment(path, "TEST_DECLARATION")
        example = decl.get("worked_example_reference")
        if example and example not in valid:
            failures.append(f"{path.relative_to(root)} -> {example}")
    if failures:
        print("\n".join(failures))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
