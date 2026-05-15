from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools._registry_paths import active_registry_path
from tools._shared import canonical_review_entry, current_package_id

ENTRY_REGISTRY = 'docs/release/PACKAGE_ENTRY_REGISTRY.yaml'


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {'true', 'false'}:
        return value == 'true'
    return value


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_entries = False
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith('#'):
            continue
        if line == 'entries:':
            in_entries = True
            continue
        if in_entries:
            if line.startswith('  - '):
                if current:
                    entries.append(current)
                current = {}
                tail = line[4:]
                if tail:
                    key, value = tail.split(':', 1)
                    current[key.strip()] = parse_scalar(value)
                continue
            if line.startswith('    '):
                assert current is not None
                key, value = line.strip().split(':', 1)
                current[key.strip()] = parse_scalar(value)
                continue
            if current:
                entries.append(current)
                current = None
            in_entries = False
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = parse_scalar(value)
    if current:
        entries.append(current)
    result['entries'] = entries
    return result


def validate(root: Path) -> list[str]:
    findings: list[str] = []
    registry_path = root / ENTRY_REGISTRY
    package_id = current_package_id(root)
    canonical_review = str(canonical_review_entry(root))
    if not registry_path.exists():
        return [f'missing package entry registry: {ENTRY_REGISTRY}']
    data = parse_simple_yaml(registry_path)
    if data.get('package_id') != package_id:
        findings.append('package entry registry has wrong package_id')
    entries = data.get('entries', [])
    canonical_by_role: dict[str, int] = {}
    for entry in entries:
        path_value = entry.get('path', '')
        role = entry.get('role', '')
        entry_status = entry.get('entry_status', '')
        canonical = bool(entry.get('canonical', False))
        path = root / path_value
        if not path.exists():
            findings.append(f'package entry registry references missing file: {path_value}')
            continue
        text = path.read_text(encoding='utf-8')
        if canonical:
            canonical_by_role[role] = canonical_by_role.get(role, 0) + 1
        if entry_status == 'canonical':
            if package_id not in text:
                findings.append(f'canonical entry missing current package id: {path_value}')
            if 'CANONICAL CURRENT' not in text and path_value != 'README.md':
                findings.append(f'canonical entry missing canonical banner: {path_value}')
        if entry_status == 'historical':
            if 'HISTORICAL ENTRY DOCUMENT' not in text:
                findings.append(f'historical entry missing historical banner: {path_value}')
            if 'superseded by' not in text.lower():
                findings.append(f'historical entry missing superseded-by pointer: {path_value}')
    for role, count in canonical_by_role.items():
        if count != 1:
            findings.append(f'entry role must have exactly one canonical document: {role} -> {count}')
    readme_text = (root / 'README.md').read_text(encoding='utf-8')
    if canonical_review not in readme_text:
        findings.append('README does not point to canonical review entry')
    start_here_text = (root / 'docs/handbook/START_HERE.md').read_text(encoding='utf-8')
    if canonical_review not in start_here_text:
        findings.append('START_HERE does not point to canonical review entry')
    manifest_text = (root / 'docs/release/RELEASE_MANIFEST.yaml').read_text(encoding='utf-8')
    if package_id not in manifest_text:
        findings.append('release manifest missing current package id')
    governance = json.loads(active_registry_path(root, 'governance_model_json').read_text(encoding='utf-8'))
    if governance.get('package_id') != package_id:
        findings.append('governance model package_id mismatch')
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
    print('package-entry validation: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
