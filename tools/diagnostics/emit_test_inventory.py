from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tools._registry_paths import active_registry_path
from tools._shared import parse_assignment


def infer_category(path: Path) -> str:
    try:
        idx = path.parts.index('tests')
        return path.parts[idx + 1]
    except (ValueError, IndexError):
        return 'uncategorized'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    rows = []
    missing_declarations: list[str] = []
    for path in sorted((root / 'tests').rglob('test_*.py')):
        try:
            declaration = parse_assignment(path, 'TEST_DECLARATION')
        except KeyError:
            missing_declarations.append(str(path.relative_to(root)))
            continue
        row = {'path': str(path.relative_to(root)), 'category': infer_category(path), **declaration}
        rows.append(row)
    rows.sort(key=lambda item: (item['category'], item['path']))

    json_out = active_registry_path(root, 'test_inventory_json')
    csv_out = active_registry_path(root, 'test_inventory_csv')
    json_out.write_text(json.dumps({'rows': rows, 'missing_test_declarations': missing_declarations}, indent=2) + '\n', encoding='utf-8')
    with csv_out.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['path', 'category', 'test_id', 'verifies_requirements', 'checks_invariants', 'worked_example_reference', 'expected_proof_output'],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                'path': row['path'],
                'category': row['category'],
                'test_id': row['test_id'],
                'verifies_requirements': '; '.join(row.get('verifies_requirements', [])),
                'checks_invariants': '; '.join(row.get('checks_invariants', [])),
                'worked_example_reference': row.get('worked_example_reference') or '',
                'expected_proof_output': row.get('expected_proof_output', ''),
            })
    print(json_out)
    print(csv_out)
    if missing_declarations:
        print('missing TEST_DECLARATION in:')
        for item in missing_declarations:
            print(f' - {item}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
