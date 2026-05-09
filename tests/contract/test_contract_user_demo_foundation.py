from __future__ import annotations

import pytest

from universaldaq.common import GraphMode, as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-057',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-003', 'UDQ-REQ-UI-006', 'UDQ-REQ-SIG-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'operator shell foundation preserves a persistent top bar, right-default docking, and first-class user-demo scenarios',
}
pytestmark = pytest.mark.contract

from universaldaq.ui import (
    GraphPanelViewModel,
    ShellViewModel,
    TrustedSessionSummary,
    FirstSignalCardViewModel,
    build_operator_shell_foundation,
    build_user_demo_mode_summary,
)


def _build_shell() -> ShellViewModel:
    return ShellViewModel(
        page='operate',
        graph_panel=GraphPanelViewModel(
            mode=GraphMode.LIVE,
            page='operate',
            visible_trace_count=3,
            status_label='interactive',
        ),
        authority_label='interactive',
        first_signal_summary=FirstSignalCardViewModel(
            signal_id='SIG-001',
            display_name='garage_temp_filtered',
            point_key='TEMP-001',
            point_class='analog',
            latest_value='21.2',
            quality_label='good',
            latest_timestamp=as_event_time(1),
            engineering_units='C',
            freshness_label='fresh',
            provenance_label='RPI_01.GPIO17 / garage_temp_filtered',
        ),
        trusted_session_summary=TrustedSessionSummary(
            lifecycle_state='connected',
            graph_status_label='live',
            live_numeric_visible=True,
            graph_visible=True,
            trace_point_count=12,
            session_event_count=4,
            ready_for_operator=True,
            signal_freshness_label='fresh',
            control_mode_label='armed_control',
            active_alarm_count=1,
            unacknowledged_alarm_count=1,
            highest_active_severity='warning',
            recent_action_count=2,
            flight_record_ready=True,
        ),
        restored_historical_context_label='restored historical context only',
        active_device=None,
        preferred_device_key='RPI_01',
        preferred_channel_key='garage_temp_filtered',
    )


def test_user_demo_mode_summary_exposes_curated_scenarios() -> None:
    summary = build_user_demo_mode_summary(active=True, active_scenario_id='logic_control_demo')

    assert summary.available is True
    assert summary.active is True
    assert summary.write_scope_label == 'demo_only'
    assert summary.scenario_count >= 4
    assert summary.active_scenario_id == 'logic_control_demo'
    assert any(item.logic_enabled for item in summary.scenarios)
    assert any(item.alarm_enabled for item in summary.scenarios)


def test_operator_shell_foundation_keeps_persistent_top_bar_and_right_default_dock() -> None:
    foundation = build_operator_shell_foundation(
        shell=_build_shell(),
        demo_active=True,
        active_scenario_id='trace_styling_demo',
    )

    assert foundation.dock_layout.control_dock_side == 'right'
    assert foundation.persistent_info_bar.visible is True
    assert foundation.persistent_info_bar.mode_badge == 'USER-DEMO'
    assert foundation.persistent_info_bar.control_posture_label == 'armed_control'
    assert foundation.persistent_info_bar.alarm_summary_label == 'alarms: 1 active / highest warning'
    assert foundation.autosave_preferences.enabled is True
    assert 'operate' in foundation.available_workspaces
    assert 'logic_designer' in foundation.available_workspaces
    assert 'session_review' in foundation.available_workspaces
    assert 'hardware' in {item.lens_id for item in foundation.signal_lenses}
    assert foundation.highlighted_trace_style.selected_highlight is True
