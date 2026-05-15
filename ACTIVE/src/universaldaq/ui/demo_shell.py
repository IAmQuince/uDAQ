from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.common import EventTime


WORKSPACE_OPERATE = 'operate'
WORKSPACE_LOGIC_DESIGNER = 'logic_designer'
WORKSPACE_SESSION_REVIEW = 'session_review'
WORKSPACE_SYSTEM = 'system'

DOCK_RIGHT = 'right'
DOCK_LEFT = 'left'
DOCK_BOTTOM = 'bottom'
DOCK_FLOATING = 'floating'


@dataclass(frozen=True, slots=True, kw_only=True)
class PersistentInfoBar:
    workspace_label: str
    runtime_label: str
    connection_label: str
    control_posture_label: str
    alarm_summary_label: str
    device_label: str
    signal_label: str
    freshness_label: str
    historical_context_label: str | None = None
    mode_badge: str | None = None
    visible: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class DockLayoutPreference:
    control_dock_side: str = DOCK_RIGHT
    bottom_panel_visible: bool = True
    explorer_dock_side: str = DOCK_LEFT
    allow_floating_panels: bool = True
    restore_default_layout_available: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class TracePresentationStyle:
    color: str
    line_width: int = 2
    line_pattern: str = 'solid'
    marker_style: str = 'none'
    marker_size: int = 0
    opacity_percent: int = 100
    glow_edge: bool = False
    selected_highlight: bool = False
    blink_mode: str = 'off'
    axis_assignment: str = 'primary'
    alarm_overlay_policy: str = 'severity_outline'
    persistable: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class LegendPresentationPreferences:
    mode: str = 'compact'
    interactive: bool = True
    show_current_value: bool = True
    show_units: bool = True
    show_alarm_badges: bool = True
    show_axis_indicator: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class GraphAutosavePreferences:
    enabled: bool = True
    interval_seconds: int = 120
    save_trace_styles: bool = True
    save_legend_preferences: bool = True
    save_named_graph_setups: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class SignalLensDescriptor:
    lens_id: str
    display_name: str
    description: str
    default_for_workspace: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDemoScenario:
    scenario_id: str
    display_name: str
    description: str
    showcased_features: tuple[str, ...]
    source_classes: tuple[str, ...]
    signal_count: int
    logic_enabled: bool = False
    alarm_enabled: bool = False
    control_enabled: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDemoModeSummary:
    available: bool
    menu_path: str
    active: bool = False
    runtime_label: str = 'simulated'
    write_scope_label: str = 'demo_only'
    pseudo_live: bool = True
    scenario_count: int = 0
    active_scenario_id: str | None = None
    active_scenario_label: str | None = None
    scenarios: tuple[UserDemoScenario, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class OperatorShellFoundation:
    persistent_info_bar: PersistentInfoBar
    default_workspace: str
    available_workspaces: tuple[str, ...]
    dock_layout: DockLayoutPreference
    signal_lenses: tuple[SignalLensDescriptor, ...]
    legend_preferences: LegendPresentationPreferences
    autosave_preferences: GraphAutosavePreferences
    user_demo_mode: UserDemoModeSummary
    highlighted_trace_style: TracePresentationStyle
    trace_style_catalog: Mapping[str, TracePresentationStyle] = field(default_factory=dict)
    generated_at: EventTime | None = None


DEFAULT_SIGNAL_LENSES: tuple[SignalLensDescriptor, ...] = (
    SignalLensDescriptor(
        lens_id='hardware',
        display_name='Hardware',
        description='Device-centric hardware and transport names.',
        default_for_workspace=WORKSPACE_OPERATE,
    ),
    SignalLensDescriptor(
        lens_id='raw',
        display_name='Raw',
        description='Raw point values and original signal identities.',
    ),
    SignalLensDescriptor(
        lens_id='logical',
        display_name='Logical',
        description='User-facing canonical tag and logical variable names.',
        default_for_workspace=WORKSPACE_LOGIC_DESIGNER,
    ),
    SignalLensDescriptor(
        lens_id='derived',
        display_name='Derived',
        description='Calculated variables, filtered values, and computed outputs.',
    ),
    SignalLensDescriptor(
        lens_id='control',
        display_name='Control',
        description='Control-module outputs, setpoints, and gated write targets.',
    ),
    SignalLensDescriptor(
        lens_id='saved',
        display_name='Saved Sets',
        description='Named graph and operator setups curated by the user.',
        default_for_workspace=WORKSPACE_SESSION_REVIEW,
    ),
)


DEFAULT_DEMO_SCENARIOS: tuple[UserDemoScenario, ...] = (
    UserDemoScenario(
        scenario_id='trace_styling_demo',
        display_name='Trace Styling Demo',
        description='Pseudo-live signals focused on line styles, legend behavior, axis assignment, and selection emphasis.',
        showcased_features=('trace_style', 'interactive_legend', 'axis_assignment', 'selection_highlight'),
        source_classes=('raw', 'logical', 'derived'),
        signal_count=8,
    ),
    UserDemoScenario(
        scenario_id='alarm_visualization_demo',
        display_name='Alarm Visualization Demo',
        description='Signals that deliberately traverse warning, high, and critical alarm tiers with visible trace overlays.',
        showcased_features=('alarm_overlay', 'legend_badges', 'event_correlation'),
        source_classes=('logical', 'derived'),
        signal_count=6,
        alarm_enabled=True,
    ),
    UserDemoScenario(
        scenario_id='signal_lineage_demo',
        display_name='Signal Lineage Demo',
        description='One raw source rendered through hardware, logical, derived, and control naming lenses without losing shared identity.',
        showcased_features=('hardware_view', 'logical_view', 'derived_view', 'control_view'),
        source_classes=('hardware', 'raw', 'logical', 'derived', 'control'),
        signal_count=5,
    ),
    UserDemoScenario(
        scenario_id='logic_control_demo',
        display_name='Logic / Control Demo',
        description='Pseudo edge inputs mapped through transforms into pseudo analog-output sinks while the operator watches values update live.',
        showcased_features=('logic_canvas', 'pseudo_live_control', 'watch_values', 'graph_feedback'),
        source_classes=('hardware', 'logical', 'control'),
        signal_count=10,
        logic_enabled=True,
        alarm_enabled=True,
        control_enabled=True,
    ),
)
