from __future__ import annotations

import pytest

from universaldaq.ui.shell_views import (
    MappingApplyWorkflowState,
    build_mapping_apply_review_panel,
)


TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-062',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-007', 'UDQ-REQ-SEC-001'],
    'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-TRANS-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'shell-facing mapping apply review hooks distinguish preflight, blocked, prepared-only, and not-executed states',
}
pytestmark = pytest.mark.contract


def test_mapping_apply_review_panel_distinguishes_preflight_pass_warning_and_blocked_states() -> None:
    passed = build_mapping_apply_review_panel(preflight_state='pass', review_text='all checks passed')
    warned = build_mapping_apply_review_panel(preflight_state='pass_with_warnings', review_text='unit warning', warning_count=1)
    blocked = build_mapping_apply_review_panel(preflight_state='stale', review_text='refresh required', blocking_count=1)

    assert passed.state == MappingApplyWorkflowState.PREFLIGHT_PASSED
    assert passed.can_prepare_request is True
    assert warned.state == MappingApplyWorkflowState.PREFLIGHT_WARNINGS
    assert warned.can_prepare_request is True
    assert warned.warning_count == 1
    assert blocked.state == MappingApplyWorkflowState.PREFLIGHT_BLOCKED
    assert blocked.can_prepare_request is False
    assert blocked.blocking_count == 1


def test_prepared_request_panel_is_explicitly_not_executed() -> None:
    panel = build_mapping_apply_review_panel(
        preflight_state='pass',
        review_text='request is ready',
        prepared_request_id='REQ-MAP-002',
        executed=False,
    )

    assert panel.state == MappingApplyWorkflowState.PREPARED_REQUEST_NOT_EXECUTED
    assert panel.prepared_request_id == 'REQ-MAP-002'
    assert panel.executed is False
    assert panel.can_prepare_request is False
    assert 'not executed' in panel.review_text.lower()
