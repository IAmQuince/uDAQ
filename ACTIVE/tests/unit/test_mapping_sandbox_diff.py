from __future__ import annotations

from universaldaq.common import as_event_time
from universaldaq.mapping import (
    MappingSandboxController,
    MappingSandboxStateStore,
    build_demo_apply_request,
    build_demo_sandbox_state,
    export_mapping_diff_markdown,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-MAPPING-SANDBOX-002',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-QUAL-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'sandbox diff report stays reviewable and explicitly non-live',
}


def test_mapping_sandbox_apply_generates_diff_without_live_execution() -> None:
    store = MappingSandboxStateStore(state=build_demo_sandbox_state())
    result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=build_demo_apply_request(),
        created_timestamp=as_event_time(5010),
    )

    assert result.accepted is True
    assert result.executed_live is False
    assert result.diff_report is not None
    assert result.diff_report.changed_count == 1
    assert result.diff_report.added_count == 1
    assert result.diff_report.total_change_count == 2


def test_mapping_diff_markdown_states_non_live_boundary() -> None:
    store = MappingSandboxStateStore(state=build_demo_sandbox_state())
    result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=build_demo_apply_request(),
        created_timestamp=as_event_time(5020),
    )

    assert result.diff_report is not None
    markdown = export_mapping_diff_markdown(result.diff_report)

    assert 'Mapping sandbox diff report' in markdown
    assert 'Live state and hardware outputs' in markdown
    assert 'SIG-DEMO-FLOW' in markdown
