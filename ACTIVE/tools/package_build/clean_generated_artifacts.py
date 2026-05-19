from __future__ import annotations

import shutil
from pathlib import Path

GENERATED_DIR_NAMES = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
GENERATED_SUFFIXES = {".pyc", ".pyo"}
TEMP_SUFFIXES = {".tmp"}


def clean(root: Path) -> int:
    removed = 0
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and path.name in GENERATED_DIR_NAMES:
            shutil.rmtree(path, ignore_errors=True)
            removed += 1
        elif path.is_file() and (path.suffix in GENERATED_SUFFIXES or path.suffix in TEMP_SUFFIXES):
            path.unlink(missing_ok=True)
            removed += 1
    return removed


if __name__ == "__main__":
    removed = clean(Path.cwd())
    print(f"removed={removed}")
