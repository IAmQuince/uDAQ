from __future__ import annotations

from dataclasses import replace

import pytest

from universaldaq.app import (
    DraftBindingRow,
    MappingApplyCoordinator,
    MappingApplyMode,
    MappingApplyRequest,
    MappingDryRunCommitState,
    MappingPreflightValidator,
    build_mapping_change_set,
    prepare_mapping_apply_request,
)
from universaldaq.common import EventTime
from universaldaq.ui.shell_views import MappingApplyWorkflowState, build_mapping_apply_review_panel


TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-063',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-SIG-001', 'UDQ-REQ-UI-007', 'UDQ-REQ-SEC-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-003', 'UDQ-INV-TRANS-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'controller dry-run commit boundary authorizes reviewed mapping requests without live mutation and rejects stale/backend-unavailable/live-mode attempts',
}
pytestmark = pytest.mark.contract


def _authoritative_row(logical_id: str, endpoint: str, *, status: str = 'applied', units: str = 'V') -> dict[str, object]:
    return {
        'logical_id': logical_id,
        'logical_display_name': logical_id,
        'direction': 'device_input_to_internal_signal',
        'source_endpoint': endpoint,
        'destination_endpoint': '',
        'status': status,
        'engineering_units': units,
        'device_identity_key': 'device::demo',
    }


def _draft(logical_id: str, endpoint: str, *, units: str = 'V') -> DraftBindingRow:
    return DraftBindingRow(
        logical_id=logical_id,
        direction='device_input_to_internal_signal',
        source_endpoint=endpoint,
        logical_display_name=logical_id,
        engineering_units=units,
        device_identity_key='device::demo',
    )


def _prepared_request(*, snapshot: EventTime = EventTime(2000), request_id: str = 'REQ-MAP-DRYRUN-001') -> tuple[MappingApplyRequest, tuple[dict[str, object], ...]]:
    authoritative_rows = (_authoritative_row('sig_voltage', 'AIN0'),)
    change_set = build_mapping_change_set(
        device_identity_key='device::demo',
        authoritative_rows=authoritative_rows,
        draft_rows=(_draft('sig_voltage', 'AIN1'),),
        authoritative_snapshot_timestamp=snapshot,
    )
    result = MappingPreflightValidator(
        known_signal_ids=frozenset({'sig_voltage'}),
        available_endpoints=frozenset({'AIN1'}),
    ).validate(change_set)
    request = prepare_mapping_apply_request(
        preflight_result=result,
        mode=MappingApplyMode.PREPARED_ONLY,
        created_timestamp=EventTime(2010),
        request_id=request_id,
    )
    return request, authoritative_rows


def test_controller_dry_run_commit_accepts_current_reviewed_request_without_mutating_authoritative_rows() -> None:
    request, authoritative_rows = _prepared_request(snapshot=EventTime(2000))

    dry_run = MappingApplyCoordinator().dry_run_commit(
        request=request,
        current_authoritative_snapshot_timestamp=EventTime(2000),
        readback_available=True,
        created_timestamp=EventTime(2020),
        execution_mode=MappingApplyMode.DRY_RUN_COMMIT,
        result_id='RESULT-MAP-001',
        audit_event_id='AUDIT-MAP-001',
    )

    assert dry_run.state == MappingDryRunCommitState.ACCEPTED
    assert dry_run.accepted is True
    assert dry_run.authorized is True
    assert dry_run.executed_live is False
    assert dry_run.would_change_count == 1
    assert dry_run.audit_event is not None
    assert dry_run.audit_event.executed_live is False
    assert dry_run.audit_event.accepted is True
    assert authoritative_rows[0]['source_endpoint'] == 'AIN0'


def test_controller_dry_run_commit_rejects_stale_prepared_request() -> None:
    request, _ = _prepared_request(snapshot=EventTime(2100))

    dry_run = MappingApplyCoordinator().dry_run_commit(
        request=request,
        current_authoritative_snapshot_timestamp=EventTime(2101),
        readback_available=True,
        created_timestamp=EventTime(2110),
        execution_mode=MappingApplyMode.DRY_RUN_COMMIT,
    )

    assert dry_run.state == MappingDryRunCommitState.STALE
    assert dry_run.accepted is False
    assert dry_run.executed_live is False
    assert 'stale' in dry_run.blocked_reason.lower()
    assert dry_run.audit_event is not None
    assert dry_run.audit_event.authorized is False


def test_controller_dry_run_commit_rejects_backend_unavailable_and_blocking_preflight_requests() -> None:
    request, _ = _prepared_request(snapshot=EventTime(2200))

    unavailable = MappingApplyCoordinator().dry_run_commit(
        request=request,
        current_authoritative_snapshot_timestamp=EventTime(2200),
        readback_available=False,
        created_timestamp=EventTime(2210),
        execution_mode=MappingApplyMode.DRY_RUN_COMMIT,
    )
    blocked_request = replace(request, preflight_state='blocked')
    blocked = MappingApplyCoordinator().dry_run_commit(
        request=blocked_request,
        current_authoritative_snapshot_timestamp=EventTime(2200),
        readback_available=True,
        created_timestamp=EventTime(2220),
        execution_mode=MappingApplyMode.DRY_RUN_COMMIT,
    )

    assert unavailable.state == MappingDryRunCommitState.BACKEND_UNAVAILABLE
    assert unavailable.executed_live is False
    assert blocked.state == MappingDryRunCommitState.REJECTED
    assert blocked.executed_live is False


def test_controller_dry_run_commit_explicitly_rejects_live_execution_modes() -> None:
    request, _ = _prepared_request(snapshot=EventTime(2300))

    rejected = MappingApplyCoordinator().dry_run_commit(
        request=request,
        current_authoritative_snapshot_timestamp=EventTime(2300),
        readback_available=True,
        created_timestamp=EventTime(2310),
        execution_mode=MappingApplyMode.EXECUTE_LIVE,
    )

    assert rejected.state == MappingDryRunCommitState.LIVE_MODE_REJECTED
    assert rejected.accepted is False
    assert rejected.executed_live is False
    assert rejected.audit_event is not None
    assert rejected.audit_event.executed_live is False


def test_shell_review_panel_distinguishes_controller_dry_run_accept_and_reject_states() -> None:
    accepted = build_mapping_apply_review_panel(
        preflight_state='pass',
        review_text='request ready',
        prepared_request_id='REQ-MAP-DRYRUN-001',
        dry_run_result_state='accepted',
        dry_run_result_id='RESULT-MAP-001',
        dry_run_would_change_count=1,
    )
    rejected = build_mapping_apply_review_panel(
        preflight_state='pass',
        review_text='request stale',
        prepared_request_id='REQ-MAP-DRYRUN-002',
        dry_run_result_state='stale',
        dry_run_result_id='RESULT-MAP-002',
        dry_run_blocked_reason='prepared request was stale',
    )

    assert accepted.state == MappingApplyWorkflowState.CONTROLLER_DRY_RUN_ACCEPTED
    assert accepted.executed is False
    assert accepted.dry_run_would_change_count == 1
    assert 'not executed live' in accepted.review_text.lower()
    assert rejected.state == MappingApplyWorkflowState.CONTROLLER_DRY_RUN_REJECTED
    assert rejected.dry_run_blocked_reason == 'prepared request was stale'
    assert 'not executed live' in rejected.review_text.lower()
