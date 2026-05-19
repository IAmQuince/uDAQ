from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .demo_builders import build_operator_shell_foundation
from .demo_shell import OperatorShellFoundation
from .viewmodels import ShellViewModel


MENU_FILE = 'file'
MENU_VIEW = 'view'
MENU_WORKSPACE = 'workspace'
MENU_MODE = 'mode'
MENU_SETTINGS = 'settings'
MENU_TESTING = 'testing'
MENU_HELP = 'help'


@dataclass(frozen=True, slots=True, kw_only=True)
class MenuActionSpec:
    action_id: str
    label: str
    checkable: bool = False
    checked: bool = False
    enabled: bool = True
    tooltip: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class MenuSpec:
    menu_id: str
    label: str
    actions: tuple[MenuActionSpec, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkspaceSpec:
    workspace_id: str
    label: str
    description: str
    user_facing: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class VisibleOperatorShellSpec:
    shell_title: str
    menus: tuple[MenuSpec, ...]
    workspaces: tuple[WorkspaceSpec, ...]
    persistent_info_bar_required: bool
    right_default_control_dock: bool
    foundation: OperatorShellFoundation
    launch_entry_point: str
    graph_engine_label: str = 'pyqtgraph'
    launchable_gui_claim: bool = True
    demo_mode_first_class: bool = True
    standard_menu_bar_required: bool = True
    settings_editable_in_app: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)


_WORKSPACE_SPECS: tuple[WorkspaceSpec, ...] = (
    WorkspaceSpec(
        workspace_id='operate',
        label='Operate',
        description='Live or demo operator workspace with graphing, signal inspection, and notes.',
    ),
    WorkspaceSpec(
        workspace_id='logic_designer',
        label='Logic Designer',
        description='Canvas-based logic and simulation workspace with pseudo-live watch values.',
    ),
    WorkspaceSpec(
        workspace_id='session_review',
        label='Session Review',
        description='Historical session review and lightweight reporting workspace.',
    ),
    WorkspaceSpec(
        workspace_id='system',
        label='System',
        description='Settings, layout, diagnostics, and shell-level preferences.',
    ),
)


def _menu(menu_id: str, label: str, actions: Iterable[MenuActionSpec]) -> MenuSpec:
    return MenuSpec(menu_id=menu_id, label=label, actions=tuple(actions))


def build_visible_operator_shell_spec(
    *,
    shell: ShellViewModel,
    demo_active: bool = True,
    active_scenario_id: str | None = 'logic_control_demo',
) -> VisibleOperatorShellSpec:
    foundation = build_operator_shell_foundation(
        shell=shell,
        demo_active=demo_active,
        active_scenario_id=active_scenario_id,
    )
    menus = (
        _menu(
            MENU_FILE,
            'File',
            (
                MenuActionSpec(action_id='file_save_graph_setup', label='Save Graph Setup…', tooltip='Persist the current graph setup and trace presentation.'),
                MenuActionSpec(action_id='file_load_graph_setup', label='Load Graph Setup…', tooltip='Restore a named graph setup.'),
                MenuActionSpec(action_id='file_export_session_report', label='Export Lightweight Session Report…', tooltip='Emit a compact human-readable session report.'),
                MenuActionSpec(action_id='file_exit', label='Exit', tooltip='Close the application.'),
            ),
        ),
        _menu(
            MENU_VIEW,
            'View',
            (
                MenuActionSpec(action_id='view_restore_default_layout', label='Restore Default Layout', tooltip='Return all panels and workspaces to the recommended default arrangement.'),
                MenuActionSpec(action_id='view_save_current_view', label='Save Current View…', tooltip='Persist the current shell layout as a named quick view.'),
                MenuActionSpec(action_id='view_manage_saved_views', label='Manage Saved Views…', tooltip='Load, overwrite, and delete named quick views.'),
                MenuActionSpec(action_id='view_reset_panel_sizes', label='Reset Panel Sizes', tooltip='Return the panel splitters to the current workspace defaults.'),
                MenuActionSpec(action_id='view_reset_layout_cache', label='Reset Layout Cache', tooltip='Discard saved window geometry and layout cache, then restore the default shell posture.'),
                MenuActionSpec(action_id='view_toggle_device_explorer', label='Device Explorer Visible', checkable=True, checked=True),
                MenuActionSpec(action_id='view_toggle_signal_explorer', label='Signal Explorer Visible', checkable=True, checked=True),
                MenuActionSpec(action_id='view_toggle_control_dock', label='Control Column Visible', checkable=True, checked=True),
                MenuActionSpec(action_id='view_toggle_bottom_log', label='Events / Diagnostics Visible', checkable=True, checked=foundation.dock_layout.bottom_panel_visible),
                MenuActionSpec(action_id='view_toggle_trace_inspector', label='Trace Inspector Visible', checkable=True, checked=True),
                MenuActionSpec(action_id='view_toggle_notes', label='Notes Visible', checkable=True, checked=True),
            ),
        ),
        _menu(
            MENU_WORKSPACE,
            'Workspace',
            tuple(
                MenuActionSpec(
                    action_id=f'workspace_{workspace.workspace_id}',
                    label=workspace.label,
                    checkable=True,
                    checked=workspace.workspace_id == foundation.default_workspace,
                    tooltip=workspace.description,
                )
                for workspace in _WORKSPACE_SPECS
            ),
        ),
        _menu(
            MENU_MODE,
            'Mode',
            (
                MenuActionSpec(action_id='mode_live', label='Live', checkable=True, checked=not demo_active, enabled=True, tooltip='Enter the live runtime path for one supported adapter and visible read-side proof.'),
                MenuActionSpec(action_id='mode_replay', label='Replay', checkable=True, checked=False, enabled=False, tooltip='Reserved for replay-driven runtime.'),
                MenuActionSpec(action_id='mode_fake', label='Fake', checkable=True, checked=False, enabled=False, tooltip='Reserved for deterministic fake-runtime mode.'),
                MenuActionSpec(action_id='mode_user_demo', label='User-Demo', checkable=True, checked=demo_active, tooltip='Enter the first-class demo runtime with pseudo-live signals and safe pseudo-control.'),
            ),
        ),
        _menu(
            MENU_SETTINGS,
            'Settings',
            (
                MenuActionSpec(action_id='settings_preferences', label='Preferences…', tooltip='Edit shell, graph, legend, and persistence preferences in-app.'),
                MenuActionSpec(action_id='settings_autosave_toggle', label='Autosave Enabled', checkable=True, checked=foundation.autosave_preferences.enabled, tooltip='Toggle automatic persistence of graph and shell setup state.'),
            ),
        ),
        _menu(
            MENU_TESTING,
            'Testing',
            (
                MenuActionSpec(action_id='testing_run_smoke', label='Run Smoke Test', tooltip='Run the safe no-hardware Sprint 1 smoke test and write a report.'),
                MenuActionSpec(action_id='testing_run_sandbox_demo', label='Run Mapping Sandbox Demo', tooltip='Apply demo mapping changes to sandbox state only and write a report.'),
                MenuActionSpec(action_id='testing_run_apply_rollback', label='Run Apply/Rollback Test', tooltip='Apply demo mapping changes, rollback, and verify the sandbox state hash is restored.'),
                MenuActionSpec(action_id='testing_run_diff_report', label='Run Diff Report Test', tooltip='Generate a human-readable mapping diff report.'),
                MenuActionSpec(action_id='testing_run_shell_wiring_audit', label='Run Visible Shell Wiring Audit', tooltip='Check visible-shell callback wiring and startup summary ordering.'),
                MenuActionSpec(action_id='testing_export_bundle', label='Export Diagnostic Bundle', tooltip='Generate an easy-to-return diagnostic bundle with acceptance reports.'),
                MenuActionSpec(action_id='testing_open_manual_checklist', label='Open Manual Test Checklist', tooltip='Open the Sprint 1 manual testing checklist.'),
                MenuActionSpec(action_id='testing_open_report_folder', label='Open Latest Report Folder', tooltip='Open the folder containing automated Sprint 1 test reports.'),
            ),
        ),
        _menu(
            MENU_HELP,
            'Help',
            (
                MenuActionSpec(action_id='help_user_demo_guide', label='User-Demo Guide', tooltip='Review the demo scenarios and what each one showcases.'),
                MenuActionSpec(action_id='help_export_diagnostics', label='Export Diagnostics', tooltip='Generate a diagnostic artifact describing visible shell state and demo posture.'),
                MenuActionSpec(action_id='help_about', label='About UniversalDAQ', tooltip='Show application and package identity information.'),
            ),
        ),
    )
    return VisibleOperatorShellSpec(
        shell_title='UniversalDAQ',
        menus=menus,
        workspaces=_WORKSPACE_SPECS,
        persistent_info_bar_required=True,
        right_default_control_dock=foundation.dock_layout.control_dock_side == 'right',
        foundation=foundation,
        launch_entry_point='tools.ui.launch_operator_shell:main',
        notes=(
            'The visible shell shall expose a persistent top information bar across all workspaces.',
            'The main control column shall default to the right while remaining dockable to the left.',
            'User-Demo mode shall remain visually distinct from live runtime posture.',
            'Live runtime posture shall be selectable from the shell while keeping read-only and armed-control states explicit.',
            'The graph engine shall be pyqtgraph with application-owned performance discipline.',
            'Device Explorer shall remain raw-hardware-facing while Signal Explorer stays internal-signal-facing.',
            'The System workspace shall surface mapping preview and draft state while canonical applied bindings remain backend-owned until controller wiring is explicit.',
            'Named saved views shall be accessible from View and persist shell workspace and panel state.',
        ),
    )
