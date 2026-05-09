from __future__ import annotations

import json
from pathlib import Path

if __name__ == "__main__":
    rows = json.loads(Path("tests/data/first_slice_requirement_pack.json").read_text(encoding="utf-8"))["requirements"]
    for row in rows:
        print(row["requirement_id"], row["intended_module_area"])
