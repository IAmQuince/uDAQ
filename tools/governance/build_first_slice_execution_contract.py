from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._registry_paths import active_registry_path
from tools._shared import load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='tests/data/first_slice_execution_contract.json')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    contract = load_json(active_registry_path(root, 'execution_contract_json'))
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(contract, indent=2) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
