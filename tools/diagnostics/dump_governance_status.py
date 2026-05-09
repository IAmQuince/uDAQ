from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._registry_paths import active_registry_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='audit_reports/active/UDQ_GOVERNANCE_STATUS__2026-03-21_235959.json')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    req = json.loads(active_registry_path(root, 'requirement_json').read_text())['requirements']
    inv = json.loads(active_registry_path(root, 'invariant_json').read_text())['rows']
    contract = json.loads(active_registry_path(root, 'execution_contract_json').read_text())['entries']
    payload = {
        'requirement_count': len(req),
        'invariant_count': len(inv),
        'execution_contract_count': len(contract),
        'ready_requirements': len([r for r in req if r['implementation_entry_status'] == 'READY_FOR_IMPLEMENTATION']),
        'ui_package_name': 'src/universaldaq/ui',
        'documentation_impact_control': 'PRESENT',
    }
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
