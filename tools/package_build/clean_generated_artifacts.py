from __future__ import annotations

from pathlib import Path

if __name__ == "__main__":
    removed = 0
    for path in Path("audit_reports/active").glob("*.tmp"):
        path.unlink()
        removed += 1
    print(f"removed={removed}")
