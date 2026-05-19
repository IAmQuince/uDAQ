from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.conftest import SRC_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-090',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'visible shell wiring hotfix rejects missing callbacks and early summary refresh ordering',
}
pytestmark = pytest.mark.contract

QT_SHELL = SRC_ROOT / 'universaldaq' / 'ui' / 'qt_shell.py'
REQUIRED_LOGIC_METHODS = {
    '_default_logic_nodes',
    '_reset_logic_nodes',
    '_add_logic_node',
    '_remove_last_logic_node',
    '_evaluate_logic_nodes',
    '_refresh_logic_watch',
    '_build_logic_demo_scene',
}


def _operator_shell_classes() -> list[ast.ClassDef]:
    tree = ast.parse(QT_SHELL.read_text(encoding='utf-8'))
    return [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == 'OperatorShellWindow']


def _method_map(cls: ast.ClassDef) -> dict[str, ast.FunctionDef]:
    return {node.name: node for node in cls.body if isinstance(node, ast.FunctionDef)}


def test_visible_shell_operator_class_has_real_logic_callbacks() -> None:
    classes = _operator_shell_classes()
    assert classes, 'OperatorShellWindow class was not found'
    active_cls = classes[-1]
    methods = _method_map(active_cls)
    missing = sorted(REQUIRED_LOGIC_METHODS.difference(methods))
    assert not missing, f'active OperatorShellWindow is missing required logic callbacks: {missing}'

    remove_method = methods['_remove_last_logic_node']
    call_names = {
        node.func.attr
        for node in ast.walk(remove_method)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert '_build_logic_demo_scene' in call_names
    assert '_refresh_logic_watch' in call_names
    assert 'showMessage' in call_names
    assert any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'pop' for node in ast.walk(remove_method))

    scene_method = methods['_build_logic_demo_scene']
    assert any(isinstance(node, ast.For) for node in ast.walk(scene_method)), 'logic scene builder must render from the draft node model'
    assert 'No draft logic nodes' in ast.get_source_segment(QT_SHELL.read_text(encoding='utf-8'), scene_method)


def test_system_summary_refresh_is_not_connected_before_system_workspace_exists() -> None:
    active_cls = _operator_shell_classes()[-1]
    build_shell = _method_map(active_cls)['_build_shell']
    source = ast.get_source_segment(QT_SHELL.read_text(encoding='utf-8'), build_shell) or ''
    system_index = source.find('self._build_system_workspace()')
    connect_index = source.find('self.workspace_tabs.currentChanged.connect(self._on_workspace_tab_changed)')
    assert system_index >= 0, 'system workspace construction not found in _build_shell'
    assert connect_index >= 0, 'workspace tab changed signal connection not found in _build_shell'
    assert system_index < connect_index, 'workspace tab change signal must be connected only after system_summary is created'


def test_system_summary_refresh_writes_meaningful_summary_not_placeholder() -> None:
    active_cls = _operator_shell_classes()[-1]
    methods = _method_map(active_cls)
    refresh = methods['_refresh_system_summary']
    source = ast.get_source_segment(QT_SHELL.read_text(encoding='utf-8'), refresh) or ''
    assert 'self.system_summary.setPlainText' in source
    assert 'UniversalDAQ Visible Operator Shell' in source
    assert 'Mapped rows:' in source
    assert 'Device I/O rows:' in source
