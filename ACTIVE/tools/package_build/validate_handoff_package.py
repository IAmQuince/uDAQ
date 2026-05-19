#!/usr/bin/env python3
"""Validate the uDAQ handoff package lane structure and identity.
Run from the package root or from ACTIVE/.
"""
from pathlib import Path
import json, sys
PACKAGE_ID = "UDQ-PKG-20260515-02-MAPPING-R02"
ROOT_NAME = "20260515_02_mapping"

def find_root(start: Path) -> Path:
    p = start.resolve()
    if (p/'ACTIVE').is_dir() and (p/'HISTORICAL').is_dir():
        return p
    if p.name == 'ACTIVE' and (p.parent/'HISTORICAL').is_dir():
        return p.parent
    for parent in p.parents:
        if (parent/'ACTIVE').is_dir() and (parent/'HISTORICAL').is_dir():
            return parent
    raise RuntimeError('Could not locate package root containing ACTIVE/ and HISTORICAL/.')

def main() -> int:
    root = find_root(Path.cwd())
    active = root/'ACTIVE'
    hist = root/'HISTORICAL'
    checks = []
    checks.append(('root_has_active', active.is_dir()))
    checks.append(('root_has_historical', hist.is_dir()))
    checks.append(('root_index', (root/'ROOT_PACKAGE_INDEX.md').is_file()))
    checks.append(('active_start', (active/'README_START_HERE.md').is_file()))
    checks.append(('historical_start', (hist/'README_HISTORICAL_ARCHIVE.md').is_file()))
    checks.append(('metadata', (active/'config'/'package_metadata.json').is_file()))
    if (active/'config'/'package_metadata.json').is_file():
        data = json.loads((active/'config'/'package_metadata.json').read_text(encoding='utf-8'))
        checks.append(('package_id_matches', data.get('package_id') == PACKAGE_ID))
    review = active/'docs'/'release'/f'REVIEW_START_HERE__{PACKAGE_ID}__ACTIVE.md'
    checks.append(('current_review_entry', review.is_file()))
    bad = [p for p in root.rglob('*') if p.name == '__pycache__' or p.suffix in {'.pyc','.pyo'}]
    checks.append(('no_generated_junk', not bad))
    print('uDAQ handoff package diagnostic')
    print('root:', root)
    for name, ok in checks:
        print(f'{name}: {"PASS" if ok else "FAIL"}')
    return 0 if all(ok for _, ok in checks) else 2
if __name__ == '__main__':
    raise SystemExit(main())
