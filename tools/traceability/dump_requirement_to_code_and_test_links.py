from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tools._registry_paths import active_registry_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-json', default='audit_reports/active/UDQ_REQUIREMENT_CODE_TEST_LINKS__2026-03-21_235959.json')
    parser.add_argument('--output-csv', default='audit_reports/active/UDQ_REQUIREMENT_CODE_TEST_LINKS__2026-03-21_235959.csv')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()

    requirements = json.loads(active_registry_path(root, 'requirement_json').read_text(encoding='utf-8'))['requirements']
    tests = json.loads(active_registry_path(root, 'test_inventory_json').read_text(encoding='utf-8'))['rows']
    rows: list[dict[str, object]] = []
    for req in requirements:
        req_id = req['requirement_id']
        linked_tests = sorted({row['test_id'] for row in tests if req_id in row.get('verifies_requirements', [])})
        linked_test_paths = sorted({row['path'] for row in tests if req_id in row.get('verifies_requirements', [])})
        rows.append({
            'requirement_id': req_id,
            'intended_module_area': req.get('intended_module_area', ''),
            'linked_test_ids': linked_tests,
            'linked_test_paths': linked_test_paths,
            'implementation_entry_status': req.get('implementation_entry_status', ''),
        })

    json_out = root / args.output_json
    csv_out = root / args.output_csv
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps({'rows': rows}, indent=2) + '\n', encoding='utf-8')
    with csv_out.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['requirement_id', 'intended_module_area', 'linked_test_ids', 'linked_test_paths', 'implementation_entry_status'],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                'requirement_id': row['requirement_id'],
                'intended_module_area': row['intended_module_area'],
                'linked_test_ids': '; '.join(row['linked_test_ids']),
                'linked_test_paths': '; '.join(row['linked_test_paths']),
                'implementation_entry_status': row['implementation_entry_status'],
            })
    print(json_out)
    print(csv_out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
