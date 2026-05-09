from __future__ import annotations

import pytest

from universaldaq.app import (
    DraftBindingRow,
    MappingApplyMode,
    MappingChangeKind,
    MappingPreflightState,
    MappingPreflightValidator,
    build_mapping_change_set,
    build_mapping_review_summary,
    prepare_mapping_apply_request,
)
from universaldaq.common import EventTime


TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-061',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-SIG-001', 'UDQ-REQ-UI-007', 'UDQ-REQ-SEC-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-003', 'UDQ-INV-TRANS-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'mapping drafts produce preflight-reviewed, non-executing apply requests without mutating authoritative readback',
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


def test_mapping_change_set_classifies_add_replace_remove_and_unchanged_without_mutating_readback() -> None:
    authoritative_rows = (
        _authoritative_row('sig_same', 'AIN0'),
        _authoritative_row('sig_replace', 'AIN1'),
        _authoritative_row('sig_remove', 'AIN2'),
    )
    draft_rows = (
        _draft('sig_same', 'AIN0'),
        _draft('sig_replace', 'AIN3'),
        _draft('sig_add', 'AIN4'),
    )

    change_set = build_mapping_change_set(
        device_identity_key='device::demo',
        authoritative_rows=authoritative_rows,
        draft_rows=draft_rows,
        authoritative_snapshot_timestamp=EventTime(1000),
    )

    kinds = {proposal.logical_id: proposal.change_kind for proposal in change_set.proposals}
    assert kinds['sig_same'] == MappingChangeKind.UNCHANGED
    assert kinds['sig_replace'] == MappingChangeKind.REPLACE
    assert kinds['sig_remove'] == MappingChangeKind.REMOVE
    assert kinds['sig_add'] == MappingChangeKind.ADD
    assert authoritative_rows[1]['source_endpoint'] == 'AIN1'


def test_preflight_blocks_stale_backend_and_missing_fields_before_request_preparation() -> None:
    change_set = build_mapping_change_set(
        device_identity_key='device::demo',
        authoritative_rows=(_authoritative_row('sig_stale', 'AIN0', status='stale'),),
        draft_rows=(_draft('sig_stale', 'AIN1'),),
        authoritative_snapshot_timestamp=None,
    )

    result = MappingPreflightValidator(known_signal_ids=frozenset({'sig_stale'}), available_endpoints=frozenset({'AIN1'})).validate(change_set)

    assert result.state == MappingPreflightState.STALE
    assert result.blocking_issues
    assert not result.can_prepare_apply_request
    with pytest.raises(ValueError):
        prepare_mapping_apply_request(preflight_result=result, created_timestamp=EventTime(1100))


def test_preflight_warns_on_unit_mismatch_but_allows_prepared_only_request() -> None:
    change_set = build_mapping_change_set(
        device_identity_key='device::demo',
        authoritative_rows=(_authoritative_row('sig_voltage', 'AIN0', units='V'),),
        draft_rows=(_draft('sig_voltage', 'AIN1', units='mV'),),
        authoritative_snapshot_timestamp=EventTime(1200),
    )

    result = MappingPreflightValidator(known_signal_ids=frozenset({'sig_voltage'}), available_endpoints=frozenset({'AIN1'})).validate(change_set)
    review = build_mapping_review_summary(result)
    request = prepare_mapping_apply_request(
        preflight_result=result,
        mode=MappingApplyMode.PREPARED_ONLY,
        created_timestamp=EventTime(1300),
        request_id='REQ-MAP-001',
    )

    assert result.state == MappingPreflightState.PASS_WITH_WARNINGS
    assert result.can_prepare_apply_request
    assert review.warning_count == 1
    assert 'UNIT_MISMATCH' not in review.text  # operator text stays readable; issue codes remain structured
    assert request.request_id == 'REQ-MAP-001'
    assert request.mode == MappingApplyMode.PREPARED_ONLY
    assert request.executed is False
    assert request.requires_confirmation is True
    assert request.authoritative_snapshot_timestamp == EventTime(1200)


def test_preflight_blocks_duplicate_endpoint_and_backend_unavailable() -> None:
    change_set = build_mapping_change_set(
        device_identity_key='device::demo',
        authoritative_rows=(),
        draft_rows=(
            _draft('sig_a', 'AIN9'),
            _draft('sig_b', 'AIN9'),
        ),
        authoritative_snapshot_timestamp=EventTime(1400),
        readback_available=False,
    )

    result = MappingPreflightValidator(known_signal_ids=frozenset({'sig_a', 'sig_b'}), available_endpoints=frozenset({'AIN9'})).validate(change_set)
    codes = {issue.code for issue in result.issues}

    assert result.state == MappingPreflightState.BACKEND_UNAVAILABLE
    assert 'BACKEND_UNAVAILABLE' in codes
    assert 'DUPLICATE_ENDPOINT' in codes
    assert not result.can_prepare_apply_request


def test_live_execute_mode_is_rejected_even_after_passing_preflight() -> None:
    change_set = build_mapping_change_set(
        device_identity_key='device::demo',
        authoritative_rows=(),
        draft_rows=(_draft('sig_new', 'AIN5'),),
        authoritative_snapshot_timestamp=EventTime(1500),
    )
    result = MappingPreflightValidator(known_signal_ids=frozenset({'sig_new'}), available_endpoints=frozenset({'AIN5'})).validate(change_set)

    assert result.state == MappingPreflightState.PASS
    with pytest.raises(ValueError):
        prepare_mapping_apply_request(preflight_result=result, mode='execute_live', created_timestamp=EventTime(1600))  # type: ignore[arg-type]
