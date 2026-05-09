from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def parse_assignment(path: Path, symbol_name: str) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == symbol_name:
                    value = ast.literal_eval(node.value)
                    if not isinstance(value, dict):
                        raise TypeError(f'{symbol_name} in {path} did not evaluate to a dict')
                    return value
    raise KeyError(f'{symbol_name} not found in {path}')


def parse_simple_yaml_scalars(path: Path) -> dict[str, Any]:
    """Parse the package's simple release YAML surfaces without external dependencies.

    This intentionally supports the scalar/list subset used by RELEASE_MANIFEST.yaml
    and PACKAGE_ENTRY_REGISTRY.yaml so governance tools can derive package identity
    from the manifest instead of hardcoding release IDs.
    """
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if line.startswith('  - ') and current_list_key:
            result.setdefault(current_list_key, []).append(line[4:].strip())
            continue
        if not line.startswith(' ') and ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value:
                result[key] = value
                current_list_key = None
            else:
                result[key] = []
                current_list_key = key
        else:
            current_list_key = None
    return result


def load_release_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / 'docs' / 'release' / 'RELEASE_MANIFEST.yaml'
    if not manifest_path.exists():
        raise FileNotFoundError(f'missing release manifest: {manifest_path}')
    return parse_simple_yaml_scalars(manifest_path)


def current_package_id(root: Path) -> str:
    package_id = load_release_manifest(root).get('package_id', '')
    if not isinstance(package_id, str) or not package_id.strip():
        raise ValueError('release manifest does not define package_id')
    return package_id.strip()


def canonical_review_entry(root: Path) -> Path:
    value = load_release_manifest(root).get('canonical_review_entry', '')
    if not isinstance(value, str) or not value.strip():
        raise ValueError('release manifest does not define canonical_review_entry')
    return Path(value.strip())
