from __future__ import annotations

from universaldaq.ui.qt_shell import build_visible_shell_spec_for_demo

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-MAPPING-SANDBOX-006',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'visible shell exposes bounded testing menu actions without implying live authority',
}


def test_visible_shell_spec_exposes_testing_menu_actions() -> None:
    spec = build_visible_shell_spec_for_demo()
    menus = {menu.menu_id: menu for menu in spec.menus}

    assert 'testing' in menus
    action_ids = {action.action_id for action in menus['testing'].actions}
    assert {
        'testing_run_smoke',
        'testing_run_sandbox_demo',
        'testing_run_apply_rollback',
        'testing_run_diff_report',
        'testing_export_session_replay_evidence',
        'testing_export_bundle',
        'testing_open_manual_checklist',
        'testing_open_report_folder',
    }.issubset(action_ids)
