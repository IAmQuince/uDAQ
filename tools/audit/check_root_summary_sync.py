from __future__ import annotations

from pathlib import Path


SUMMARY_FILES = [
    'docs/release/EXEC_SUMMARY.md',
    'docs/handbook/IMPLEMENTATION_ENTRY.md',
]


def main() -> int:
    root = Path('.').resolve()
    for rel in SUMMARY_FILES:
        path = root / rel
        if not path.exists():
            print(f'missing summary file: {rel}')
            return 1
    print('root-summary sync assets present')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
