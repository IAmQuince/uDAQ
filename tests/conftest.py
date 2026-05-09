from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from tools._registry_paths import active_registry_path
REGISTRY_ROOT = PACKAGE_ROOT / 'registries' / 'active'
DATA_ROOT = PACKAGE_ROOT / 'tests' / 'data'
SRC_ROOT = PACKAGE_ROOT / 'src'
if importlib.util.find_spec('universaldaq') is None and str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def parse_declaration(path: Path, symbol_name: str) -> dict[str, Any]:
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


@pytest.fixture(scope='session')
def requirement_registry() -> dict[str, Any]:
    return load_json(active_registry_path(PACKAGE_ROOT, 'requirement_json'))


@pytest.fixture(scope='session')
def invariant_registry() -> dict[str, Any]:
    return load_json(active_registry_path(PACKAGE_ROOT, 'invariant_json'))


@pytest.fixture(scope='session')
def execution_contract() -> dict[str, Any]:
    return load_json(active_registry_path(PACKAGE_ROOT, 'execution_contract_json'))


@pytest.fixture(scope='session')
def first_slice_requirement_pack() -> dict[str, Any]:
    return load_json(DATA_ROOT / 'first_slice_requirement_pack.json')
