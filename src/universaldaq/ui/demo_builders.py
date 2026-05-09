from __future__ import annotations

from dataclasses import asdict

from universaldaq.common import as_event_time

from .demo_shell import (
    DEFAULT_DEMO_SCENARIOS,
    DEFAULT_SIGNAL_LENSES,
    DOCK_RIGHT,
    GraphAutosavePreferences,
    LegendPresentationPreferences,
    OperatorShellFoundation,
    PersistentInfoBar,
    TracePresentationStyle,
    UserDemoModeSummary,
    WORKSPACE_LOGIC_DESIGNER,
    WORKSPACE_OPERATE,
    WORKSPACE_SESSION_REVIEW,
    WORKSPACE_SYSTEM,
    DockLayoutPreference,
)
from .viewmodels import ShellViewModel


def build_user_demo_mode_summary(*, active: bool = False, active_scenario_id: str | None = None) -> UserDemoModeSummary:
    active_scenario = next((item for item in DEFAULT_DEMO_SCENARIOS if item.scenario_id == active_scenario_id), None)
    return UserDemoModeSummary(
        available=True,
        menu_path='Mode > User-Demo',
        active=active,
        scenario_count=len(DEFAULT_DEMO_SCENARIOS),
        active_scenario_id=None if active_scenario is None else active_scenario.scenario_id,
        active_scenario_label=None if active_scenario is None else active_scenario.display_name,
        scenarios=DEFAULT_DEMO_SCENARIOS,
    )


def build_persistent_info_bar(*, shell: ShellViewModel, demo_mode: UserDemoModeSummary | None = None) -> PersistentInfoBar:
    trusted = shell.trusted_session_summary
    first_signal = shell.first_signal_summary
    workspace_label = shell.page.replace('_', ' ').title()
    runtime_label = 'user-demo' if demo_mode and demo_mode.active else shell.graph_panel.mode.value
    connection_label = shell.device_phase.replace('_', ' ')
    control_posture = 'view_only' if trusted is None else trusted.control_mode_label
    if trusted is None:
        alarm_summary = 'alarms: none'
    else:
        highest = trusted.highest_active_severity or 'none'
        alarm_summary = f'alarms: {trusted.active_alarm_count} active / highest {highest}'
    if shell.active_device is None:
        device_label = shell.preferred_device_key or 'no device selected'
    else:
        device_label = shell.active_device.display_name
    if first_signal is None:
        signal_label = shell.preferred_channel_key or 'no active signal'
        freshness_label = 'pending'
    else:
        signal_label = first_signal.display_name
        freshness_label = first_signal.freshness_label
    historical_context_label = shell.restored_historical_context_label
    mode_badge = None
    if demo_mode and demo_mode.active:
        mode_badge = 'USER-DEMO'
    elif shell.last_restore_origin is not None:
        mode_badge = f'RESTORE:{shell.last_restore_origin}'
    return PersistentInfoBar(
        workspace_label=workspace_label,
        runtime_label=runtime_label,
        connection_label=connection_label,
        control_posture_label=control_posture,
        alarm_summary_label=alarm_summary,
        device_label=device_label,
        signal_label=signal_label,
        freshness_label=freshness_label,
        historical_context_label=historical_context_label,
        mode_badge=mode_badge,
    )


def build_operator_shell_foundation(*, shell: ShellViewModel, demo_active: bool = False, active_scenario_id: str | None = None) -> OperatorShellFoundation:
    demo = build_user_demo_mode_summary(active=demo_active, active_scenario_id=active_scenario_id)
    trace_style_catalog = {
        'default': TracePresentationStyle(color='#5dade2', line_width=2),
        'selected': TracePresentationStyle(
            color='#f5b041',
            line_width=3,
            glow_edge=True,
            selected_highlight=True,
            axis_assignment='primary',
        ),
        'secondary_axis': TracePresentationStyle(
            color='#af7ac5',
            line_width=2,
            line_pattern='dashed',
            axis_assignment='secondary',
        ),
        'alarm_warning': TracePresentationStyle(
            color='#5dade2',
            line_width=2,
            glow_edge=True,
            alarm_overlay_policy='warning_outline',
        ),
        'alarm_critical': TracePresentationStyle(
            color='#5dade2',
            line_width=3,
            glow_edge=True,
            blink_mode='critical_only',
            alarm_overlay_policy='critical_outline',
        ),
    }
    return OperatorShellFoundation(
        persistent_info_bar=build_persistent_info_bar(shell=shell, demo_mode=demo),
        default_workspace=WORKSPACE_OPERATE,
        available_workspaces=(WORKSPACE_OPERATE, WORKSPACE_LOGIC_DESIGNER, WORKSPACE_SESSION_REVIEW, WORKSPACE_SYSTEM),
        dock_layout=DockLayoutPreference(control_dock_side=DOCK_RIGHT),
        signal_lenses=DEFAULT_SIGNAL_LENSES,
        legend_preferences=LegendPresentationPreferences(),
        autosave_preferences=GraphAutosavePreferences(enabled=True),
        user_demo_mode=demo,
        highlighted_trace_style=trace_style_catalog['selected'],
        trace_style_catalog=trace_style_catalog,
        generated_at=as_event_time(0),
    )


def dump_operator_shell_foundation_dict(*, shell: ShellViewModel, demo_active: bool = False, active_scenario_id: str | None = None) -> dict[str, object]:
    foundation = build_operator_shell_foundation(
        shell=shell,
        demo_active=demo_active,
        active_scenario_id=active_scenario_id,
    )
    data = asdict(foundation)
    data['available_workspaces'] = list(foundation.available_workspaces)
    data['signal_lenses'] = [asdict(item) for item in foundation.signal_lenses]
    data['user_demo_mode']['scenarios'] = [asdict(item) for item in foundation.user_demo_mode.scenarios]
    data['trace_style_catalog'] = {key: asdict(value) for key, value in foundation.trace_style_catalog.items()}
    return data
