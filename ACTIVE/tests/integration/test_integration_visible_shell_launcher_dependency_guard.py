from __future__ import annotations

import pytest

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-041',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'visible shell launcher fails clearly when optional GUI dependencies are unavailable',
}
pytestmark = pytest.mark.integration


def test_visible_shell_launcher_returns_clear_guard_code_when_gui_dependencies_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    from universaldaq.ui import qt_shell

    monkeypatch.setattr(qt_shell, 'detect_gui_dependencies', lambda: {'PySide6': False, 'pyqtgraph': False})

    result = qt_shell.launch_visible_operator_shell(initial_scenario_id='logic_control_demo')

    assert result == 2
