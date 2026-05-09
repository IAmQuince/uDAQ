from __future__ import annotations

import argparse, json
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    args = parser.parse_args()
    data = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
    required = {"proof_id", "scenario", "generated_by"}
    missing = required - data.keys()
    if missing:
        print(sorted(missing))
        raise SystemExit(1)
    print("OK")
