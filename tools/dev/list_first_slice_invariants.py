from __future__ import annotations

import json
from pathlib import Path

if __name__ == "__main__":
    rows = json.loads(Path("tests/data/first_slice_invariant_registry.json").read_text(encoding="utf-8"))["rows"]
    for row in rows:
        print(row["invariant_id"], row["title"])
