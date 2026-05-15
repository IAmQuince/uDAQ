from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._registry_paths import ACTIVE_REGISTRIES, active_registry_path

REQUIRED_KEYS = [
    'ID:',
    'Status:',
    'Revision:',
    'Owner:',
    'Authority:',
    'Source docs:',
]


def validate(root: Path) -> list[str]:
    findings: list[str] = []
    registry_path = active_registry_path(root, 'readme_json')
    if not registry_path.exists():
        return [f'missing README registry: {ACTIVE_REGISTRIES.readme_json}']
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    for row in registry['rows']:
        path = root / row['path']
        if not path.exists():
            findings.append(f"missing controlled entry document: {row['path']}")
            continue
        text = path.read_text(encoding='utf-8')
        for key in REQUIRED_KEYS:
            if key not in text:
                findings.append(f"{row['path']} missing control field: {key}")
        if row['authority_level'] == 'DERIVED' and 'Source docs:' not in text:
            findings.append(f"{row['path']} missing derived source-doc declaration")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    findings = validate(root)
    if findings:
        for item in findings:
            print(item)
        return 1
    print('readme-control validation: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
