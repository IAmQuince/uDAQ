from __future__ import annotations

import pytest

from universaldaq.ui.demo_runtime import DemoRuntimeEngine
from universaldaq.ui.shell_views import (
    ShellLayoutSnapshot,
    ShellViewCatalog,
    build_device_io_rows,
    build_mapping_rows,
    derive_event_console_rows,
    summarize_device_io_rows,
    summarize_mapping_rows,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-059',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-004', 'UDQ-REQ-UI-007'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'shell saved-view defaults and mapping rows remain explicit and non-overlapping',
}
pytestmark = pytest.mark.contract


def test_shell_view_catalog_exposes_expected_built_in_defaults() -> None:
    catalog = ShellViewCatalog.default()
    assert {'Bench Default', 'Trend Focus', 'Logic Workbench', 'Review + Notes', 'Alarm Watch'}.issubset(set(catalog.names()))


def test_shell_layout_snapshot_round_trips_losslessly() -> None:
    snapshot = ShellLayoutSnapshot(workspace_id='system', explorer_tab_id='device', control_tab_id='diagnostics')
    recovered = ShellLayoutSnapshot.from_dict(snapshot.to_dict())
    assert recovered == snapshot


def test_mapping_rows_keep_device_and_signal_surfaces_distinct() -> None:
    runtime = DemoRuntimeEngine(scenario_id='logic_control_demo')
    rows = build_mapping_rows(signal_descriptors=runtime.signal_descriptors(), runtime_mode='USER-DEMO')
    summary = summarize_mapping_rows(rows)
    assert rows
    assert any(row.direction.value == 'device_input_to_internal_signal' for row in rows)
    assert any(row.direction.value == 'internal_signal_to_device_output' for row in rows)
    assert all(row.source_endpoint != row.internal_signal_name or row.direction.value == 'internal_signal_to_device_output' for row in rows)
    assert summary.total_count == len(rows)
    assert summary.output_count >= 1


def test_device_io_rows_keep_tagging_and_authority_on_one_canonical_row_model() -> None:
    runtime = DemoRuntimeEngine(scenario_id='logic_control_demo')
    mapping_rows = build_mapping_rows(signal_descriptors=runtime.signal_descriptors(), runtime_mode='USER-DEMO')
    rows = build_device_io_rows(
        device_context_key='demo::logic_control_demo',
        signal_descriptors=runtime.signal_descriptors(),
        mapping_rows=mapping_rows,
        authoritative_rows=(),
        tag_names_by_signal={'sig_demo_temp_0': 'stack_temp'},
        runtime_mode='USER-DEMO',
        health_label='simulated',
    )
    summary = summarize_device_io_rows(rows)
    assert rows
    assert any(row.tag_name == 'stack_temp' for row in rows)
    assert all(row.endpoint_label for row in rows)
    assert summary.total_count == len(rows)
    assert summary.input_count >= 1


def test_event_console_rows_collapse_identical_consecutive_messages() -> None:
    rows = derive_event_console_rows(
        [
            'capability survey: generic baseline active',
            'capability survey: generic baseline active',
            'connected: Visible Runtime Specimen',
        ],
        elapsed_seconds=1.0,
    )
    assert len(rows) == 2
    assert rows[0].message.endswith('(x2)')


def test_device_io_rows_distinguish_authoritative_applied_draft_modified_stale_and_unavailable_states() -> None:
    runtime = DemoRuntimeEngine(scenario_id='logic_control_demo')
    descriptors = runtime.signal_descriptors()
    mapping_rows = build_mapping_rows(signal_descriptors=descriptors, runtime_mode='USER-DEMO')
    mapping_rows_without_wave = tuple(row for row in mapping_rows if row.row_id != 'sig_demo_wave_0')
    authoritative_rows = (
        {
            'logical_id': 'sig_demo_temp_0',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'EDGE_01.ANALOG_TEMP0',
            'destination_endpoint': '',
            'status': 'applied',
            'note': 'backend applied binding readback',
        },
        {
            'logical_id': 'sig_demo_pressure_0',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'EDGE_01.REASSIGNED_ANALOG_0',
            'destination_endpoint': '',
            'status': 'applied',
            'note': 'backend applied binding differs from local draft',
        },
        {
            'logical_id': 'sig_demo_flow_0',
            'direction': 'device_input_to_internal_signal',
            'source_endpoint': 'EDGE_01.ANALOG_1',
            'destination_endpoint': '',
            'status': 'stale',
            'note': 'backend reports stale point inventory',
        },
    )

    rows = build_device_io_rows(
        device_context_key='demo::logic_control_demo',
        signal_descriptors=descriptors,
        mapping_rows=mapping_rows_without_wave,
        authoritative_rows=authoritative_rows,
        runtime_mode='USER-DEMO',
        health_label='simulated',
    )
    states_by_signal = {row.signal_id: row.authority_state for row in rows}
    summary = summarize_device_io_rows(rows)

    assert states_by_signal['sig_demo_temp_0'] == 'applied'
    assert states_by_signal['sig_demo_pressure_0'] == 'modified'
    assert states_by_signal['sig_demo_flow_0'] == 'stale'
    assert states_by_signal['sig_demo_dac_cmd'] == 'draft'
    assert states_by_signal['sig_demo_wave_0'] == 'unavailable'
    assert summary.applied_count >= 1
    assert summary.modified_count == 1
    assert summary.stale_count == 1
    assert summary.draft_count >= 1
    assert summary.unavailable_count >= 1
