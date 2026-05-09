from __future__ import annotations

import pytest

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-058',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-002', 'UDQ-REQ-UI-003', 'UDQ-REQ-UI-004', 'UDQ-REQ-UI-007'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'visible shell specification preserves standard program menus, persistent top information bar, right-default docking, and first-class demo workspaces',
}
pytestmark = pytest.mark.contract

from universaldaq.ui.qt_shell import build_visible_shell_spec_for_demo
from universaldaq.ui.visible_shell import MENU_FILE, MENU_HELP, MENU_MODE, MENU_SETTINGS, MENU_VIEW, MENU_WORKSPACE


def test_visible_shell_spec_exposes_standard_program_menus_and_workspaces() -> None:
    spec = build_visible_shell_spec_for_demo(active_scenario_id='logic_control_demo')

    menu_ids = {menu.menu_id for menu in spec.menus}
    assert {MENU_FILE, MENU_VIEW, MENU_WORKSPACE, MENU_MODE, MENU_SETTINGS, MENU_HELP}.issubset(menu_ids)
    assert spec.persistent_info_bar_required is True
    assert spec.right_default_control_dock is True
    assert spec.standard_menu_bar_required is True
    assert spec.demo_mode_first_class is True
    assert spec.graph_engine_label == 'pyqtgraph'

    workspace_ids = {workspace.workspace_id for workspace in spec.workspaces}
    assert {'operate', 'logic_designer', 'session_review', 'system'}.issubset(workspace_ids)

    mode_menu = next(menu for menu in spec.menus if menu.menu_id == MENU_MODE)
    assert any(action.action_id == 'mode_user_demo' and action.checked for action in mode_menu.actions)
    assert any(action.action_id == 'mode_live' and action.enabled is True for action in mode_menu.actions)


def test_visible_shell_spec_keeps_right_default_dock_and_user_demo_notes() -> None:
    spec = build_visible_shell_spec_for_demo(active_scenario_id='trace_styling_demo')

    assert spec.foundation.dock_layout.control_dock_side == 'right'
    assert spec.foundation.user_demo_mode.active is True
    assert spec.foundation.user_demo_mode.active_scenario_id == 'trace_styling_demo'
    assert spec.foundation.persistent_info_bar.mode_badge == 'USER-DEMO'
    assert spec.foundation.persistent_info_bar.visible is True
    assert any('persistent top information bar' in note for note in spec.notes)
    assert any('User-Demo mode' in note for note in spec.notes)
    assert any('Live runtime posture' in note for note in spec.notes)


def test_visible_shell_spec_exposes_saved_view_and_panel_visibility_actions() -> None:
    spec = build_visible_shell_spec_for_demo(active_scenario_id='logic_control_demo')
    view_menu = next(menu for menu in spec.menus if menu.menu_id == MENU_VIEW)
    action_ids = {action.action_id for action in view_menu.actions}
    assert {
        'view_save_current_view',
        'view_manage_saved_views',
        'view_reset_panel_sizes',
        'view_toggle_device_explorer',
        'view_toggle_signal_explorer',
        'view_toggle_trace_inspector',
        'view_toggle_notes',
    }.issubset(action_ids)
