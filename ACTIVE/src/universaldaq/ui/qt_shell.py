from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

from universaldaq.common import GraphMode, as_event_time

from .demo_runtime import DemoRuntimeEngine
from .live_runtime import LiveRuntimeEngine
from .layout_state import (
    LAYOUT_SCHEMA_VERSION,
    Rect,
    clamp_pip_rect,
    clamp_window_rect,
    default_graph_presentation_for_workspace,
    default_pip_rect,
    default_window_rect,
    deserialize_rect,
    normalize_splitter_sizes,
    serialize_rect,
)
from .viewmodels import FirstSignalCardViewModel, GraphPanelViewModel, ShellViewModel, TrustedSessionSummary
from .visible_shell import VisibleOperatorShellSpec, build_visible_operator_shell_spec
from .shell_views import (
    ShellViewCatalog,
    build_device_io_rows,
    build_mapping_rows,
    derive_event_console_rows,
    summarize_device_io_rows,
    summarize_mapping_rows,
)


_GUI_SETTINGS_ORG = 'ScottTools'
_GUI_SETTINGS_APP = 'UniversalDAQ'


def detect_gui_dependencies() -> dict[str, bool]:
    return {
        'PySide6': importlib.util.find_spec('PySide6') is not None,
        'pyqtgraph': importlib.util.find_spec('pyqtgraph') is not None,
    }


def default_demo_shell_viewmodel() -> ShellViewModel:
    return ShellViewModel(
        page='operate',
        graph_panel=GraphPanelViewModel(
            mode=GraphMode.LIVE,
            page='operate',
            visible_trace_count=4,
            status_label='interactive',
        ),
        authority_label='interactive',
        first_signal_summary=FirstSignalCardViewModel(
            signal_id='SIG-DEMO-001',
            display_name='garage_temp_filtered',
            point_key='TEMP-001',
            point_class='analog',
            latest_value='21.2',
            quality_label='simulated',
            latest_timestamp=as_event_time(1),
            engineering_units='C',
            freshness_label='simulated',
            provenance_label='Demo Device / garage_temp_filtered',
        ),
        trusted_session_summary=TrustedSessionSummary(
            lifecycle_state='connected',
            graph_status_label='live',
            live_numeric_visible=True,
            graph_visible=True,
            trace_point_count=12,
            session_event_count=3,
            ready_for_operator=True,
            signal_freshness_label='simulated',
            control_mode_label='view_only',
            active_alarm_count=1,
            unacknowledged_alarm_count=1,
            highest_active_severity='warning',
            recent_action_count=2,
            flight_record_ready=True,
        ),
        preferred_device_key='DEMO-FIRST-SIGNAL-001',
        preferred_channel_key='garage_temp_filtered',
        restored_historical_context_label='demo runtime context only',
    )


def build_visible_shell_spec_for_demo(*, active_scenario_id: str = 'logic_control_demo') -> VisibleOperatorShellSpec:
    return build_visible_operator_shell_spec(
        shell=default_demo_shell_viewmodel(),
        demo_active=True,
        active_scenario_id=active_scenario_id,
    )


def _pen_from_style(pg: Any, QtCore: Any, style_dict: dict[str, Any], *, color_override: str | None = None, width_offset: int = 0) -> Any:
    color = color_override or style_dict.get('color', '#5dade2')
    width = max(1, int(style_dict.get('line_width', 2)) + width_offset)
    pattern = style_dict.get('line_pattern', 'solid')
    qt_style = {
        'solid': QtCore.Qt.SolidLine,
        'dashed': QtCore.Qt.DashLine,
        'dotted': QtCore.Qt.DotLine,
    }.get(pattern, QtCore.Qt.SolidLine)
    return pg.mkPen(color=color, width=width, style=qt_style)


class _TraceState:
    __slots__ = ('signal_id', 'style', 'visible', 'selected', 'main_item', 'overlay_item')

    def __init__(self, *, signal_id: str, style: dict[str, Any], visible: bool = True) -> None:
        self.signal_id = signal_id
        self.style = style
        self.visible = visible
        self.selected = False
        self.main_item: Any | None = None
        self.overlay_item: Any | None = None


def launch_visible_operator_shell(*, initial_scenario_id: str = 'logic_control_demo', diagnostics_path: str | None = None, bench_mode: bool = False) -> int:
    deps = detect_gui_dependencies()
    if not all(deps.values()):
        missing = ', '.join(name for name, present in deps.items() if not present)
        print(
            'UniversalDAQ visible shell requires the optional UI dependencies.\n'
            f'Missing: {missing}\n'
            'Install with: python -m pip install -e .[ui] or python -m pip install PySide6 pyqtgraph',
        )
        return 2

    os.environ.setdefault('QT_ENABLE_HIGHDPI_SCALING', '1')
    os.environ.setdefault('QT_AUTO_SCREEN_SCALE_FACTOR', '1')

    from PySide6 import QtCore, QtGui, QtWidgets
    import pyqtgraph as pg

    pg.setConfigOptions(antialias=False)

    class PreferencesDialog(QtWidgets.QDialog):
        def __init__(self, parent: 'OperatorShellWindow') -> None:
            super().__init__(parent)
            self.setWindowTitle('Preferences')
            self.setModal(True)
            self._parent = parent
            self._autosave_checkbox = QtWidgets.QCheckBox('Enable autosave for layout and graph setup state')
            self._autosave_checkbox.setChecked(parent.autosave_enabled)
            self._autosave_interval = QtWidgets.QSpinBox()
            self._autosave_interval.setRange(15, 3600)
            self._autosave_interval.setSuffix(' s')
            self._autosave_interval.setValue(parent.autosave_interval_seconds)
            self._restore_layout_checkbox = QtWidgets.QCheckBox('Restore last window layout on startup')
            self._restore_layout_checkbox.setChecked(True)
            form = QtWidgets.QFormLayout()
            form.addRow(self._autosave_checkbox)
            form.addRow('Autosave interval', self._autosave_interval)
            form.addRow(self._restore_layout_checkbox)
            buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout = QtWidgets.QVBoxLayout(self)
            layout.addLayout(form)
            layout.addWidget(buttons)

        def accept(self) -> None:
            self._parent.autosave_enabled = self._autosave_checkbox.isChecked()
            self._parent.autosave_interval_seconds = int(self._autosave_interval.value())
            self._parent._configure_autosave_timer()
            self._parent._save_settings()
            super().accept()

    class PipOverlayWidget(QtWidgets.QFrame):
        def __init__(self, *, parent: QtWidgets.QWidget, on_expand: Any, on_hide: Any) -> None:
            super().__init__(parent)
            self.setObjectName('pipGraphOverlay')
            self.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.setAutoFillBackground(True)
            self.setStyleSheet('QFrame#pipGraphOverlay { background: rgba(21, 25, 31, 235); border: 1px solid #425466; border-radius: 8px; }')
            self.setMinimumSize(280, 180)
            self._drag_active = False
            self._resize_active = False
            self._press_offset = QtCore.QPoint()
            outer = QtWidgets.QVBoxLayout(self)
            outer.setContentsMargins(6, 6, 6, 6)
            outer.setSpacing(4)
            header = QtWidgets.QFrame()
            header.setObjectName('pipGraphHeader')
            header.setCursor(QtCore.Qt.OpenHandCursor)
            header_layout = QtWidgets.QHBoxLayout(header)
            header_layout.setContentsMargins(4, 2, 4, 2)
            header_layout.setSpacing(4)
            self.title_label = QtWidgets.QLabel('Compact Graph')
            header_layout.addWidget(self.title_label, 1)
            expand_btn = QtWidgets.QToolButton()
            expand_btn.setText('Expand')
            expand_btn.clicked.connect(on_expand)
            hide_btn = QtWidgets.QToolButton()
            hide_btn.setText('Hide')
            hide_btn.clicked.connect(on_hide)
            header_layout.addWidget(expand_btn)
            header_layout.addWidget(hide_btn)
            outer.addWidget(header)
            self.header = header
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
            self.plot_widget.setBackground('#11161d')
            self.plot_widget.setMenuEnabled(False)
            self.plot_widget.hideButtons()
            self.plot_widget.setLabel('bottom', 't', units='s')
            self.plot_widget.setLabel('left', 'Value')
            outer.addWidget(self.plot_widget, 1)
            grip_row = QtWidgets.QHBoxLayout()
            grip_row.addStretch(1)
            self.size_grip = QtWidgets.QSizeGrip(self)
            grip_row.addWidget(self.size_grip, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
            outer.addLayout(grip_row)
            self.header.installEventFilter(self)

        def eventFilter(self, watched: Any, event: Any) -> bool:
            if watched is self.header:
                if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
                    self._drag_active = True
                    self._press_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    self.header.setCursor(QtCore.Qt.ClosedHandCursor)
                    return True
                if event.type() == QtCore.QEvent.MouseMove and self._drag_active:
                    self.move(event.globalPosition().toPoint() - self._press_offset)
                    parent = self.parentWidget()
                    if parent is not None and hasattr(parent.window(), '_clamp_and_commit_pip_geometry'):
                        parent.window()._clamp_and_commit_pip_geometry()
                    return True
                if event.type() == QtCore.QEvent.MouseButtonRelease and self._drag_active:
                    self._drag_active = False
                    self.header.setCursor(QtCore.Qt.OpenHandCursor)
                    parent = self.parentWidget()
                    if parent is not None and hasattr(parent.window(), '_save_settings'):
                        parent.window()._save_settings()
                    return True
            return super().eventFilter(watched, event)

        def resizeEvent(self, event: Any) -> None:
            super().resizeEvent(event)
            parent = self.parentWidget()
            if parent is not None and hasattr(parent.window(), '_clamp_and_commit_pip_geometry'):
                parent.window()._clamp_and_commit_pip_geometry()

    class OperatorShellWindow(QtWidgets.QMainWindow):
        def __init__(self, *, spec: VisibleOperatorShellSpec, diagnostics_path: str | None = None, bench_mode: bool = False) -> None:
            super().__init__()
            self.spec = spec
            self.demo_runtime = DemoRuntimeEngine(scenario_id=initial_scenario_id)
            self.live_runtime = LiveRuntimeEngine()
            self.control_posture = 'view_only'
            self._last_guard_decision = None
            self.settings = QtCore.QSettings(_GUI_SETTINGS_ORG, _GUI_SETTINGS_APP)
            env_diagnostics_path = os.environ.get('UNIVERSALDAQ_SHELL_DIAGNOSTICS_PATH')
            self._diagnostics_path = None if not (diagnostics_path or env_diagnostics_path) else Path(diagnostics_path or env_diagnostics_path).expanduser().resolve()
            self._bench_mode = bool(bench_mode or os.environ.get('UNIVERSALDAQ_BENCH_MODE') == '1')
            self._bench_runbook_path = os.environ.get('UNIVERSALDAQ_BENCH_RUNBOOK_PATH')
            self.runtime_mode = self.settings.value('runtime/mode', 'USER-DEMO', type=str)
            self.runtime = self.demo_runtime if self.runtime_mode != 'LIVE' else self.live_runtime
            self.autosave_enabled = self.settings.value('ui/autosave_enabled', spec.foundation.autosave_preferences.enabled, type=bool)
            self.autosave_interval_seconds = self.settings.value('ui/autosave_interval_seconds', spec.foundation.autosave_preferences.interval_seconds, type=int)
            self.selected_lens_id = self.settings.value('ui/selected_lens_id', 'logical', type=str)
            self.selected_workspace_id = self.settings.value('ui/selected_workspace', spec.foundation.default_workspace, type=str)
            self._notes: list[str] = []
            self._trace_states: dict[str, _TraceState] = {}
            self._active_signal_id: str | None = None
            self._legend_rows: dict[str, QtWidgets.QTreeWidgetItem] = {}
            self._trace_name_by_signal: dict[str, str] = {}
            self._tag_names_by_signal = self._load_tag_names()
            self._selected_device_context_key: str | None = None
            self._selected_device_context_label: str = 'No device selected'
            self._device_io_rows: list[dict[str, Any]] = []
            self._logic_nodes: list[dict[str, Any]] = []
            self._logic_last_outputs: dict[str, float] = {}
            self._logic_nodes = self._default_logic_nodes()
            self._graph_setups = self._load_graph_setups()
            self._saved_views = ShellViewCatalog.from_json(self.settings.value('ui/saved_views_json', '', type=str))
            self._mapping_rows: dict[str, dict[str, Any]] = {}
            self._event_rows: list[dict[str, str]] = []
            self._ui_built = False
            self._layout_schema_version = LAYOUT_SCHEMA_VERSION
            self._graph_presentation_override: str | None = None
            self._graph_presentation = default_graph_presentation_for_workspace(self.selected_workspace_id)
            self._pip_rect: Rect | None = None
            self._live_device_records_by_key: dict[str, Any] = {}
            self._authoritative_binding_rows: tuple[dict[str, Any], ...] = ()
            self._authoritative_binding_status = 'unavailable'
            self.setWindowTitle(f'{spec.shell_title} — Visible Operator Shell')
            self._build_shell()
            self._restore_settings()
            self._refresh_signal_inventory()
            self._ensure_default_trace_selection()
            self._apply_workspace_selection(self.selected_workspace_id)
            self._build_logic_demo_scene()
            self._ui_built = True
            if self._bench_mode:
                self.statusBar().showMessage('Desktop bench mode active — diagnostics will be written on exit', 5000)
            self._render_step()
            self._start_timers()

        def _build_shell(self) -> None:
            self._build_menus()
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)
            root_layout = QtWidgets.QVBoxLayout(central)
            root_layout.setContentsMargins(6, 6, 6, 6)
            root_layout.setSpacing(6)
            self.top_bar = self._build_top_bar()
            root_layout.addWidget(self.top_bar)
            self.workspace_tabs = QtWidgets.QTabWidget()
            self.workspace_host = QtWidgets.QFrame()
            self.workspace_host.setObjectName('workspaceHost')
            workspace_host_layout = QtWidgets.QVBoxLayout(self.workspace_host)
            workspace_host_layout.setContentsMargins(0, 0, 0, 0)
            workspace_host_layout.setSpacing(0)
            workspace_host_layout.addWidget(self.workspace_tabs, 1)
            self._build_operate_workspace()
            self._build_logic_workspace()
            self._build_session_review_workspace()
            self._build_system_workspace()
            self.workspace_tabs.currentChanged.connect(self._on_workspace_tab_changed)
            self._build_right_control_dock()
            self._build_bottom_log_dock()
            self._build_explorer_dock()
            self.center_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
            self.center_splitter.setChildrenCollapsible(False)
            self.center_splitter.addWidget(self.workspace_host)
            self.center_splitter.addWidget(self.bottom_dock)
            self.center_splitter.setStretchFactor(0, 1)
            self.center_splitter.setStretchFactor(1, 0)
            self.outer_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            self.outer_splitter.setChildrenCollapsible(False)
            self.outer_splitter.addWidget(self.explorer_dock)
            self.outer_splitter.addWidget(self.center_splitter)
            self.outer_splitter.addWidget(self.control_dock)
            self.outer_splitter.setStretchFactor(0, 0)
            self.outer_splitter.setStretchFactor(1, 1)
            self.outer_splitter.setStretchFactor(2, 0)
            root_layout.addWidget(self.outer_splitter, 1)
            self.pip_overlay = PipOverlayWidget(parent=self.workspace_host, on_expand=self._toggle_graph_primary_overlay, on_hide=self._hide_graph_overlay)
            self.pip_overlay.hide()
            self._reset_panel_sizes()
            self.statusBar().showMessage('Ready')

        def _mode_badge(self) -> str:
            return 'USER-DEMO' if self.runtime_mode == 'USER-DEMO' else 'LIVE'

        def _switch_runtime_mode(self, mode: str) -> None:
            self.runtime_mode = mode
            self.runtime = self.demo_runtime if mode != 'LIVE' else self.live_runtime
            self.control_posture = 'view_only' if mode == 'LIVE' else self.control_posture
            if hasattr(self, 'runtime_state_label'):
                self.runtime_state_label.setText(f'{self._mode_badge()} / {getattr(self.runtime, "runtime_source_label", "simulated")}')
            self.settings.setValue('runtime/mode', self.runtime_mode)
            self._sync_mode_menu_checks()
            self._refresh_live_device_inventory()
            self._clear_plot_state()
            self._refresh_signal_inventory()
            self._ensure_default_trace_selection()
            self._render_step()

        def _sync_mode_menu_checks(self) -> None:
            for action_id, mode in (('mode_user_demo', 'USER-DEMO'), ('mode_live', 'LIVE')):
                action = self._menu_actions.get(action_id)
                if action is not None:
                    action.setChecked(self.runtime_mode == mode)

        def _clear_plot_state(self) -> None:
            for item in list(self._trace_states.values()):
                self.plot_widget.removeItem(item.main_item)
                self.plot_widget.removeItem(item.overlay_item)
            self._trace_states.clear()
            self._legend_rows.clear()
            self.legend_tree.clear()
            if hasattr(self, 'pip_overlay'):
                self.pip_overlay.plot_widget.clear()
            self._active_signal_id = None

        def _refresh_live_device_inventory(self) -> None:
            if not hasattr(self, 'live_device_combo'):
                return
            self.live_device_combo.blockSignals(True)
            self.live_device_combo.clear()
            self._live_device_records_by_key = {}
            for device in self.live_runtime.available_devices():
                self._live_device_records_by_key[device.device_key] = device
                label = f'{device.display_name} [{device.hardware_mode} / {device.capability_mode}]'
                self.live_device_combo.addItem(label, device.device_key)
            self.live_device_combo.blockSignals(False)
            self._refresh_capability_summary()

        def _selected_live_device_key(self) -> str | None:
            if not hasattr(self, 'live_device_combo'):
                return None
            return self.live_device_combo.currentData()

        def _selected_capability_record(self):
            device_key = self._selected_live_device_key()
            if not device_key:
                return None
            return getattr(self, '_live_device_records_by_key', {}).get(device_key)

        def _refresh_capability_summary(self) -> None:
            if not hasattr(self, 'capability_summary_label'):
                return
            record = self._selected_capability_record()
            if record is None:
                if getattr(self, 'live_device_combo', None) is not None and self.live_device_combo.count() > 0:
                    summary = 'Select a live device to inspect capability state'
                    reason = 'Capability state is available after you choose a discovered device.'
                else:
                    summary = 'No live devices discovered yet'
                    reason = 'Generic discovery remains active. If a support pack is absent, limited capability reporting may still appear when a device is detected.'
            else:
                summary = f"{record.capability_mode} / {record.identity_state} / {record.read_state} / {record.write_state}"
                reason = record.limited_access_reason or 'No access limitation reported for the selected device.'
            self.capability_summary_label.setText(summary)
            self.capability_reason_label.setText(reason)

        def _build_menus(self) -> None:
            menu_bar = self.menuBar()
            self._menu_actions: dict[str, QtGui.QAction] = {}
            for menu_spec in self.spec.menus:
                menu = menu_bar.addMenu(menu_spec.label)
                for action_spec in menu_spec.actions:
                    action = QtGui.QAction(action_spec.label, self)
                    action.setCheckable(action_spec.checkable)
                    if action_spec.checkable:
                        action.setChecked(action_spec.checked)
                    action.setEnabled(action_spec.enabled)
                    if action_spec.tooltip:
                        action.setToolTip(action_spec.tooltip)
                    self._menu_actions[action_spec.action_id] = action
                    menu.addAction(action)
            self._menu_actions['file_exit'].triggered.connect(self.close)
            self._menu_actions['file_save_graph_setup'].triggered.connect(self._save_graph_setup_interactive)
            self._menu_actions['file_load_graph_setup'].triggered.connect(self._load_graph_setup_interactive)
            self._menu_actions['file_export_session_report'].triggered.connect(self._export_lightweight_report)
            self._menu_actions['view_restore_default_layout'].triggered.connect(self._restore_default_layout)
            self._menu_actions['view_save_current_view'].triggered.connect(self._save_current_view_interactive)
            self._menu_actions['view_manage_saved_views'].triggered.connect(self._manage_saved_views_interactive)
            self._menu_actions['view_reset_panel_sizes'].triggered.connect(self._reset_panel_sizes)
            if 'view_reset_layout_cache' in self._menu_actions:
                self._menu_actions['view_reset_layout_cache'].triggered.connect(self._reset_layout_cache)
            self._menu_actions['view_toggle_device_explorer'].triggered.connect(self._toggle_device_explorer_tab)
            self._menu_actions['view_toggle_signal_explorer'].triggered.connect(self._toggle_signal_explorer_tab)
            self._menu_actions['view_toggle_control_dock'].triggered.connect(self._toggle_control_dock)
            self._menu_actions['view_toggle_bottom_log'].triggered.connect(self._toggle_bottom_dock)
            self._menu_actions['view_toggle_trace_inspector'].triggered.connect(self._toggle_trace_inspector_tab)
            self._menu_actions['view_toggle_notes'].triggered.connect(self._toggle_notes_tab)
            self._menu_actions['settings_preferences'].triggered.connect(self._open_preferences)
            self._menu_actions['settings_autosave_toggle'].triggered.connect(self._toggle_autosave_from_menu)
            self._menu_actions['help_export_diagnostics'].triggered.connect(self._export_diagnostics)
            self._menu_actions['help_about'].triggered.connect(self._show_about)
            self._menu_actions['help_user_demo_guide'].triggered.connect(self._show_demo_guide)
            if 'testing_run_smoke' in self._menu_actions:
                self._menu_actions['testing_run_smoke'].triggered.connect(lambda: self._run_testing_action('smoke'))
            if 'testing_run_sandbox_demo' in self._menu_actions:
                self._menu_actions['testing_run_sandbox_demo'].triggered.connect(lambda: self._run_testing_action('sandbox_demo'))
            if 'testing_run_apply_rollback' in self._menu_actions:
                self._menu_actions['testing_run_apply_rollback'].triggered.connect(lambda: self._run_testing_action('apply_rollback'))
            if 'testing_run_diff_report' in self._menu_actions:
                self._menu_actions['testing_run_diff_report'].triggered.connect(lambda: self._run_testing_action('diff_report'))
            if 'testing_run_shell_wiring_audit' in self._menu_actions:
                self._menu_actions['testing_run_shell_wiring_audit'].triggered.connect(lambda: self._run_testing_action('visible_shell_wiring_audit'))
            if 'testing_export_bundle' in self._menu_actions:
                self._menu_actions['testing_export_bundle'].triggered.connect(lambda: self._run_testing_action('diagnostic_bundle'))
            if 'testing_open_manual_checklist' in self._menu_actions:
                self._menu_actions['testing_open_manual_checklist'].triggered.connect(self._open_manual_test_checklist)
            if 'testing_open_report_folder' in self._menu_actions:
                self._menu_actions['testing_open_report_folder'].triggered.connect(self._open_latest_test_report_folder)
            self._menu_actions['mode_user_demo'].triggered.connect(self._ensure_demo_mode)
            self._menu_actions['mode_live'].triggered.connect(self._ensure_live_mode)
            for workspace in self.spec.workspaces:
                action = self._menu_actions.get(f'workspace_{workspace.workspace_id}')
                if action is not None:
                    action.triggered.connect(lambda checked=False, ws=workspace.workspace_id: self._apply_workspace_selection(ws))

        def _testing_package_root(self) -> Path:
            from universaldaq.testing import package_root_from
            return package_root_from(Path.cwd())

        def _run_testing_action(self, action_id: str) -> None:
            from universaldaq.testing import (
                export_diagnostic_bundle,
                run_apply_rollback_test,
                run_diff_report_test,
                run_mapping_sandbox_demo,
                run_smoke_test,
                run_visible_shell_wiring_audit,
            )
            runners = {
                'smoke': run_smoke_test,
                'sandbox_demo': run_mapping_sandbox_demo,
                'apply_rollback': run_apply_rollback_test,
                'diff_report': run_diff_report_test,
                'visible_shell_wiring_audit': run_visible_shell_wiring_audit,
                'diagnostic_bundle': export_diagnostic_bundle,
            }
            runner = runners.get(action_id)
            if runner is None:
                QtWidgets.QMessageBox.warning(self, 'Testing', f'Unknown testing action: {action_id}')
                return
            self.statusBar().showMessage(f'Running testing action: {action_id}…')
            try:
                result = runner(package_root=self._testing_package_root())
            except Exception as exc:  # pragma: no cover - GUI defensive path
                self.statusBar().showMessage(f'Testing action failed: {exc}', 10000)
                QtWidgets.QMessageBox.critical(self, 'Testing action failed', str(exc))
                return
            level = QtWidgets.QMessageBox.Information if result.passed else QtWidgets.QMessageBox.Warning
            message = QtWidgets.QMessageBox(level, 'Testing result', f'{result.summary}\n\nReport: {result.report_path}', QtWidgets.QMessageBox.Ok, self)
            open_button = message.addButton('Open Report', QtWidgets.QMessageBox.ActionRole)
            message.exec()
            if message.clickedButton() is open_button:
                from universaldaq.testing import open_path_best_effort
                open_path_best_effort(result.report_path)
            self.statusBar().showMessage(result.summary, 8000)

        def _open_manual_test_checklist(self) -> None:
            active_root = self._testing_package_root() / 'ACTIVE'
            checklist = active_root / 'docs' / 'testing' / '20260515_02_manual-test-checklist.md'
            if not checklist.is_file():
                QtWidgets.QMessageBox.warning(self, 'Manual Test Checklist', f'Checklist not found: {checklist}')
                return
            from universaldaq.testing import open_path_best_effort
            opened = open_path_best_effort(checklist)
            self.statusBar().showMessage(f'Manual checklist: {checklist}' if opened else f'Open manually: {checklist}', 8000)

        def _open_latest_test_report_folder(self) -> None:
            folder = self._testing_package_root() / 'ACTIVE' / 'audit_reports' / 'testing'
            folder.mkdir(parents=True, exist_ok=True)
            from universaldaq.testing import open_path_best_effort
            opened = open_path_best_effort(folder)
            self.statusBar().showMessage(f'Testing report folder: {folder}' if opened else f'Open manually: {folder}', 8000)

        def _build_top_bar(self) -> QtWidgets.QFrame:
            frame = QtWidgets.QFrame()
            frame.setObjectName('persistentInfoBar')
            frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
            layout = QtWidgets.QHBoxLayout(frame)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(12)
            self._top_bar_labels: dict[str, Any] = {}
            self._top_bar_badges: dict[str, QtWidgets.QFrame] = {}
            badge_order = (
                ('mode', 'Mode'),
                ('session', 'Session'),
                ('device', 'Device/Scenario'),
                ('signal', 'Signal'),
                ('freshness', 'Freshness'),
                ('graph', 'Graph'),
                ('access', 'Access'),
                ('control', 'Control'),
                ('alarms', 'Alarms'),
            )
            for key, title in badge_order:
                badge = QtWidgets.QFrame()
                badge.setObjectName(f'topBadge_{key}')
                badge.setFrameShape(QtWidgets.QFrame.Box)
                badge_layout = QtWidgets.QHBoxLayout(badge)
                badge_layout.setContentsMargins(6, 2, 6, 2)
                badge_layout.setSpacing(6)
                title_label = QtWidgets.QLabel(f'{title}:')
                badge_layout.addWidget(title_label)
                if key == 'graph':
                    value = QtWidgets.QToolButton()
                    value.setPopupMode(QtWidgets.QToolButton.InstantPopup)
                    value.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
                    value.setAutoRaise(True)
                    menu = QtWidgets.QMenu(value)
                    for mode_id, label in (('primary', 'Primary'), ('compact_pip', 'PiP'), ('hidden', 'Hidden')):
                        action = menu.addAction(label)
                        action.triggered.connect(lambda checked=False, mode=mode_id: self._set_graph_mode_from_top_bar(mode))
                    value.setMenu(menu)
                    value.setToolTip('Choose graph presentation mode')
                else:
                    value = QtWidgets.QLabel('—')
                    value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                value.setObjectName(f'topBar_{key}')
                badge_layout.addWidget(value)
                layout.addWidget(badge)
                self._top_bar_labels[key] = value
                self._top_bar_badges[key] = badge
            layout.addStretch(1)
            return frame

        def _set_graph_mode_from_top_bar(self, mode: str) -> None:
            if mode == 'hidden':
                self._graph_presentation_override = 'hidden'
                self._apply_graph_presentation('hidden')
                return
            self._graph_presentation_override = mode
            self._apply_graph_presentation(mode)

        def _badge_palette(self, semantic: str) -> tuple[str, str, str]:
            palettes = {
                'good': ('#123524', '#1f7a4c', '#dff8e7'),
                'info': ('#15263d', '#2d6cdf', '#e7f1ff'),
                'warning': ('#3a2610', '#c98a16', '#fff4d8'),
                'critical': ('#431b1b', '#d94848', '#ffe3e3'),
                'muted': ('#232831', '#5c6773', '#d6dde6'),
                'neutral': ('#2b313a', '#7a8795', '#eef2f7'),
            }
            return palettes.get(semantic, palettes['neutral'])

        def _apply_badge_semantics(self, key: str, semantic: str) -> None:
            badge = self._top_bar_badges.get(key)
            if badge is None:
                return
            background, border, foreground = self._badge_palette(semantic)
            badge.setStyleSheet(
                f"QFrame#{badge.objectName()} {{ background: {background}; border: 1px solid {border}; border-radius: 6px; }}"
                f" QLabel {{ color: {foreground}; font-weight: 600; }}"
                f" QToolButton {{ color: {foreground}; font-weight: 700; background: transparent; border: none; padding: 0 2px; }}"
            )

        def _refresh_top_bar_semantics(self) -> None:
            mode_text = str(self._top_bar_labels.get('mode').text()).lower() if 'mode' in self._top_bar_labels else ''
            session_text = str(self._top_bar_labels.get('session').text()).lower() if 'session' in self._top_bar_labels else ''
            freshness_text = str(self._top_bar_labels.get('freshness').text()).lower() if 'freshness' in self._top_bar_labels else ''
            access_text = str(self._top_bar_labels.get('access').text()).lower() if 'access' in self._top_bar_labels else ''
            control_text = str(self._top_bar_labels.get('control').text()).lower() if 'control' in self._top_bar_labels else ''
            alarms_text = str(self._top_bar_labels.get('alarms').text()).lower() if 'alarms' in self._top_bar_labels else ''
            graph_text = str(self._graph_presentation).lower()
            self._apply_badge_semantics('mode', 'good' if mode_text == 'live' else 'info' if mode_text == 'user-demo' else 'muted')
            if 'disconnect' in session_text or 'failed' in session_text:
                self._apply_badge_semantics('session', 'critical')
            elif 'degraded' in session_text or 'pending' in session_text:
                self._apply_badge_semantics('session', 'warning')
            elif 'connected' in session_text:
                self._apply_badge_semantics('session', 'good')
            else:
                self._apply_badge_semantics('session', 'neutral')
            self._apply_badge_semantics('device', 'neutral')
            self._apply_badge_semantics('signal', 'neutral')
            if 'stale' in freshness_text or 'invalid' in freshness_text:
                self._apply_badge_semantics('freshness', 'critical')
            elif 'degraded' in freshness_text or 'aging' in freshness_text or 'pending' in freshness_text:
                self._apply_badge_semantics('freshness', 'warning')
            elif freshness_text in {'fresh', 'simulated'}:
                self._apply_badge_semantics('freshness', 'good' if freshness_text == 'fresh' else 'info')
            else:
                self._apply_badge_semantics('freshness', 'neutral')
            self._apply_badge_semantics('graph', 'muted' if graph_text == 'hidden' else 'info' if graph_text == 'compact_pip' else 'good')
            if 'unavailable' in access_text or 'missing' in access_text:
                self._apply_badge_semantics('access', 'critical')
            elif 'limited' in access_text or 'pending' in access_text or 'unknown' in access_text:
                self._apply_badge_semantics('access', 'warning')
            elif 'writable' in access_text or 'live' in access_text:
                self._apply_badge_semantics('access', 'good')
            elif 'readable' in access_text or 'simulated' in access_text:
                self._apply_badge_semantics('access', 'info')
            else:
                self._apply_badge_semantics('access', 'neutral')
            self._apply_badge_semantics('control', 'good' if control_text == 'armed_control' else 'warning' if control_text == 'view_only' else 'critical')
            if '0 active' in alarms_text or 'none' in alarms_text:
                self._apply_badge_semantics('alarms', 'muted')
            elif 'critical' in alarms_text or 'high' in alarms_text:
                self._apply_badge_semantics('alarms', 'critical')
            elif 'warning' in alarms_text or 'active' in alarms_text:
                self._apply_badge_semantics('alarms', 'warning')
            else:
                self._apply_badge_semantics('alarms', 'neutral')

        def _build_operate_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
            summary = QtWidgets.QFrame()
            summary_layout = QtWidgets.QHBoxLayout(summary)
            summary_layout.setContentsMargins(8, 6, 8, 6)
            self.active_signal_label = QtWidgets.QLabel('No active signal')
            self.active_signal_label.setStyleSheet('font-weight: 600; font-size: 15px;')
            self.active_value_label = QtWidgets.QLabel('—')
            self.active_value_label.setStyleSheet('font-weight: 700; font-size: 18px;')
            self.active_meta_label = QtWidgets.QLabel('Quality: simulated | Provenance: demo')
            summary_layout.addWidget(self.active_signal_label, 2)
            summary_layout.addWidget(self.active_value_label, 1)
            summary_layout.addWidget(self.active_meta_label, 3)
            layout.addWidget(summary)
            self.operate_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            splitter = self.operate_splitter
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.showGrid(x=True, y=True, alpha=0.18)
            self.plot_widget.setBackground('w')
            self.plot_widget.setLabel('bottom', 'Time', units='s')
            self.plot_widget.setLabel('left', 'Value')
            self.plot_widget.addLegend(offset=(10, 10))
            splitter.addWidget(self.plot_widget)
            self.legend_tree = QtWidgets.QTreeWidget()
            self.legend_tree.setHeaderLabels(['Trace', 'Value', 'Axis', 'State'])
            self.legend_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.legend_tree.itemSelectionChanged.connect(self._on_legend_selection_changed)
            self.legend_tree.itemChanged.connect(self._on_legend_item_changed)
            self.legend_tree.setMinimumWidth(180)
            splitter.addWidget(self.legend_tree)
            splitter.setSizes([1100, 260])
            layout.addWidget(splitter, 1)
            self.workspace_tabs.addTab(page, 'Operate')

        def _build_logic_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            self.logic_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            splitter = self.logic_splitter
            palette_panel = QtWidgets.QWidget()
            palette_layout = QtWidgets.QVBoxLayout(palette_panel)
            palette_layout.setContentsMargins(0, 0, 0, 0)
            self.logic_palette = QtWidgets.QListWidget()
            self.logic_palette.addItems(['Source', 'Filter', 'Math', 'Comparator', 'Sink'])
            self.logic_palette.itemDoubleClicked.connect(lambda item: self._add_logic_node(item.text()))
            add_logic_button = QtWidgets.QPushButton('Add Draft Node')
            add_logic_button.clicked.connect(lambda: self._add_logic_node(self.logic_palette.currentItem().text() if self.logic_palette.currentItem() else 'Source'))
            remove_logic_button = QtWidgets.QPushButton('Remove Last Node')
            remove_logic_button.clicked.connect(self._remove_last_logic_node)
            reset_logic_button = QtWidgets.QPushButton('Reset Draft Chain')
            reset_logic_button.clicked.connect(self._reset_logic_nodes)
            palette_layout.addWidget(self.logic_palette, 1)
            palette_layout.addWidget(add_logic_button)
            palette_layout.addWidget(remove_logic_button)
            palette_layout.addWidget(reset_logic_button)
            splitter.addWidget(palette_panel)
            self.logic_scene = QtWidgets.QGraphicsScene()
            self.logic_view = QtWidgets.QGraphicsView(self.logic_scene)
            splitter.addWidget(self.logic_view)
            self.logic_inspector = QtWidgets.QTreeWidget()
            self.logic_inspector.setHeaderLabels(['Property', 'Value'])
            splitter.addWidget(self.logic_inspector)
            splitter.setSizes([180, 760, 260])
            layout.addWidget(splitter, 1)
            self.logic_watch = QtWidgets.QPlainTextEdit()
            self.logic_watch.setReadOnly(True)
            self.logic_watch.setMaximumHeight(180)
            layout.addWidget(self.logic_watch)
            self.workspace_tabs.addTab(page, 'Logic Designer')

        def _build_session_review_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(page)
            self.session_review_list = QtWidgets.QListWidget()
            self.session_review_detail = QtWidgets.QPlainTextEdit()
            self.session_review_detail.setReadOnly(True)
            layout.addWidget(self.session_review_list, 1)
            layout.addWidget(self.session_review_detail, 2)
            self.workspace_tabs.addTab(page, 'Session Review')
            self.session_review_list.addItems(['Current demo session', 'Last exported graph setup'])
            self.session_review_list.currentTextChanged.connect(lambda text: self.session_review_detail.setPlainText(self._review_detail_text(text)))
            self.session_review_list.setCurrentRow(0)

        def _build_system_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
            self.system_summary = QtWidgets.QPlainTextEdit()
            self.system_summary.setReadOnly(True)
            splitter.addWidget(self.system_summary)

            device_panel = QtWidgets.QWidget()
            device_layout = QtWidgets.QVBoxLayout(device_panel)
            device_layout.setContentsMargins(0, 0, 0, 0)
            self.device_io_scope_label = QtWidgets.QLabel('Device I/O Inspector — select a device to inspect its full I/O inventory and assign tags')
            self.device_io_scope_label.setStyleSheet('font-weight: 600;')
            device_layout.addWidget(self.device_io_scope_label)
            device_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            self.device_io_table = QtWidgets.QTableWidget(0, 8)
            self.device_io_table.setHorizontalHeaderLabels(['Endpoint', 'Internal Signal', 'Tag', 'Direction', 'Class', 'Access', 'Authority', 'Units'])
            self.device_io_table.horizontalHeader().setStretchLastSection(True)
            self.device_io_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.device_io_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.device_io_table.itemSelectionChanged.connect(self._on_device_io_selection_changed)
            device_splitter.addWidget(self.device_io_table)
            editor = QtWidgets.QWidget()
            editor_form = QtWidgets.QFormLayout(editor)
            self.device_io_context_label = QtWidgets.QLabel('No device selected')
            self.device_io_endpoint_label = QtWidgets.QLabel('—')
            self.device_io_internal_label = QtWidgets.QLabel('—')
            self.device_io_tag_edit = QtWidgets.QLineEdit()
            self.device_io_tag_edit.setPlaceholderText('Canonical tag / display name')
            self.device_io_tag_edit.editingFinished.connect(self._apply_device_tag_edit)
            self.device_io_authority_label = QtWidgets.QLabel('—')
            self.device_io_capability_label = QtWidgets.QLabel('—')
            self.device_io_note_label = QtWidgets.QLabel('Select an I/O row to inspect provenance, authority, and health')
            self.device_io_note_label.setWordWrap(True)
            apply_tag_button = QtWidgets.QPushButton('Apply Tag')
            apply_tag_button.clicked.connect(self._apply_device_tag_edit)
            editor_form.addRow('Context', self.device_io_context_label)
            editor_form.addRow('Endpoint', self.device_io_endpoint_label)
            editor_form.addRow('Internal Signal', self.device_io_internal_label)
            editor_form.addRow('Tag', self.device_io_tag_edit)
            editor_form.addRow('Authority', self.device_io_authority_label)
            editor_form.addRow('Access', self.device_io_capability_label)
            editor_form.addRow('Notes', self.device_io_note_label)
            editor_form.addRow(apply_tag_button)
            device_splitter.addWidget(editor)
            device_splitter.setSizes([860, 320])
            device_layout.addWidget(device_splitter, 1)
            splitter.addWidget(device_panel)

            self.authoritative_binding_summary = QtWidgets.QPlainTextEdit()
            self.authoritative_binding_summary.setReadOnly(True)
            self.authoritative_binding_summary.setMaximumHeight(150)
            splitter.addWidget(self.authoritative_binding_summary)

            mapping_panel = QtWidgets.QWidget()
            mapping_layout = QtWidgets.QVBoxLayout(mapping_panel)
            mapping_layout.setContentsMargins(0, 0, 0, 0)
            self.mapping_scope_label = QtWidgets.QLabel('Mapping Drafts / Preview — backend authority remains outside the shell')
            self.mapping_scope_label.setStyleSheet('font-weight: 600;')
            mapping_layout.addWidget(self.mapping_scope_label)
            mapping_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            self.mapping_table = QtWidgets.QTableWidget(0, 7)
            self.mapping_table.setHorizontalHeaderLabels(['Direction', 'Source Endpoint', 'Internal Signal', 'Destination Endpoint', 'Status', 'Units', 'Enabled'])
            self.mapping_table.horizontalHeader().setStretchLastSection(True)
            self.mapping_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.mapping_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.mapping_table.itemSelectionChanged.connect(self._on_mapping_selection_changed)
            mapping_splitter.addWidget(self.mapping_table)
            editor = QtWidgets.QWidget()
            editor_form = QtWidgets.QFormLayout(editor)
            self.mapping_direction_combo = QtWidgets.QComboBox(); self.mapping_direction_combo.addItems(['device_input_to_internal_signal', 'internal_signal_to_device_output'])
            self.mapping_source_combo = QtWidgets.QComboBox()
            self.mapping_internal_name_edit = QtWidgets.QLineEdit()
            self.mapping_destination_combo = QtWidgets.QComboBox()
            self.mapping_scale_spin = QtWidgets.QDoubleSpinBox(); self.mapping_scale_spin.setRange(-1_000_000, 1_000_000); self.mapping_scale_spin.setDecimals(4); self.mapping_scale_spin.setValue(1.0)
            self.mapping_offset_spin = QtWidgets.QDoubleSpinBox(); self.mapping_offset_spin.setRange(-1_000_000, 1_000_000); self.mapping_offset_spin.setDecimals(4)
            self.mapping_invert_checkbox = QtWidgets.QCheckBox('Invert signal')
            self.mapping_enabled_checkbox = QtWidgets.QCheckBox('Mapping enabled'); self.mapping_enabled_checkbox.setChecked(True)
            self.mapping_note_edit = QtWidgets.QPlainTextEdit(); self.mapping_note_edit.setPlaceholderText('Notes / provenance'); self.mapping_note_edit.setMaximumHeight(90)
            self.mapping_status_label = QtWidgets.QLabel('No draft selected — backend-applied mappings are not edited here yet')
            button_row = QtWidgets.QHBoxLayout()
            apply_button = QtWidgets.QPushButton('Save Draft Edit'); apply_button.clicked.connect(self._apply_mapping_edit)
            remove_button = QtWidgets.QPushButton('Mark Draft Unmapped'); remove_button.clicked.connect(self._remove_mapping)
            button_row.addWidget(apply_button)
            button_row.addWidget(remove_button)
            editor_form.addRow('Direction', self.mapping_direction_combo)
            editor_form.addRow('Source endpoint', self.mapping_source_combo)
            editor_form.addRow('Internal signal', self.mapping_internal_name_edit)
            editor_form.addRow('Destination endpoint', self.mapping_destination_combo)
            editor_form.addRow('Scale', self.mapping_scale_spin)
            editor_form.addRow('Offset', self.mapping_offset_spin)
            editor_form.addRow(self.mapping_invert_checkbox)
            editor_form.addRow(self.mapping_enabled_checkbox)
            editor_form.addRow('Status', self.mapping_status_label)
            editor_form.addRow('Notes', self.mapping_note_edit)
            editor_form.addRow(button_row)
            mapping_splitter.addWidget(editor)
            mapping_splitter.setSizes([860, 340])
            mapping_layout.addWidget(mapping_splitter, 1)
            splitter.addWidget(mapping_panel)
            splitter.setSizes([150, 360, 140, 340])
            layout.addWidget(splitter, 1)
            self.workspace_tabs.addTab(page, 'System')
            self._refresh_system_summary()

        def _build_right_control_dock(self) -> None:
            self.control_tabs = QtWidgets.QTabWidget()
            self.control_tab_indexes: dict[str, int] = {}
            self.control_tab_indexes['session'] = self.control_tabs.addTab(self._build_session_panel(), 'Session')
            self.control_tab_indexes['signals'] = self.control_tabs.addTab(self._build_signals_panel(), 'Signals')
            self.control_tab_indexes['trace'] = self.control_tabs.addTab(self._build_trace_inspector_panel(), 'Trace Inspector')
            self.control_tab_indexes['notes'] = self.control_tabs.addTab(self._build_notes_panel(), 'Notes')
            self.control_tab_indexes['diagnostics'] = self.control_tabs.addTab(self._build_diagnostics_panel(), 'Diagnostics')
            self.control_dock = self._wrap_panel('Control Column', self.control_tabs)
            self.control_dock.setMinimumWidth(240)

        def _build_bottom_log_dock(self) -> None:
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(4, 4, 4, 4)
            toolbar = QtWidgets.QHBoxLayout()
            self.event_filter_combo = QtWidgets.QComboBox()
            self.event_filter_combo.addItems(['All', 'Diagnostics', 'Actions', 'Warnings', 'Alarms', 'Runtime'])
            self.event_filter_combo.currentTextChanged.connect(self._refresh_event_console)
            self.event_search_edit = QtWidgets.QLineEdit()
            self.event_search_edit.setPlaceholderText('Search events…')
            self.event_search_edit.textChanged.connect(self._refresh_event_console)
            toolbar.addWidget(QtWidgets.QLabel('Filter'))
            toolbar.addWidget(self.event_filter_combo)
            toolbar.addWidget(self.event_search_edit, 1)
            layout.addLayout(toolbar)
            self.event_table = QtWidgets.QTableWidget(0, 4)
            self.event_table.setHorizontalHeaderLabels(['Time', 'Severity', 'Category', 'Message'])
            self.event_table.horizontalHeader().setStretchLastSection(True)
            self.event_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.event_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.bottom_log = QtWidgets.QPlainTextEdit()
            self.bottom_log.setReadOnly(True)
            self.bottom_log.setMaximumHeight(90)
            self.bottom_log.hide()
            layout.addWidget(self.event_table, 1)
            layout.addWidget(self.bottom_log)
            self.bottom_dock = self._wrap_panel('Events / Diagnostics', container)
            self.bottom_dock.setMinimumHeight(150)

        def _build_explorer_dock(self) -> None:
            self.explorer_tabs = QtWidgets.QTabWidget()
            self.device_explorer = QtWidgets.QTreeWidget()
            self.device_explorer.setHeaderLabels(['Device / Endpoint', 'Capability', 'Runtime'])
            self.device_explorer.setMinimumWidth(180)
            self.device_explorer.itemSelectionChanged.connect(self._on_device_explorer_selection_changed)
            self.signal_explorer = QtWidgets.QTreeWidget()
            self.signal_explorer.setHeaderLabels(['Internal Signal', 'Source', 'Status'])
            self.logic_explorer = QtWidgets.QTreeWidget()
            self.logic_explorer.setHeaderLabels(['Logic / Mapping Surface'])
            self.explorer_tab_indexes: dict[str, int] = {}
            self.explorer_tab_indexes['device'] = self.explorer_tabs.addTab(self.device_explorer, 'Device Explorer')
            self.explorer_tab_indexes['signal'] = self.explorer_tabs.addTab(self.signal_explorer, 'Signal Explorer')
            self.explorer_tab_indexes['logic'] = self.explorer_tabs.addTab(self.logic_explorer, 'Logic Modules')
            self.explorer_dock = self._wrap_panel('Explorers', self.explorer_tabs)
            self.explorer_dock.setMinimumWidth(210)

        def _wrap_panel(self, title: str, child: QtWidgets.QWidget) -> QtWidgets.QFrame:
            panel = QtWidgets.QFrame()
            panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
            layout = QtWidgets.QVBoxLayout(panel)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(4)
            heading = QtWidgets.QLabel(title)
            heading.setStyleSheet('font-weight: 600; padding: 2px 4px;')
            layout.addWidget(heading)
            layout.addWidget(child, 1)
            return panel

        def _build_session_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QFormLayout(panel)
            self.demo_scenario_combo = QtWidgets.QComboBox()
            for scenario in self.demo_runtime.available_scenarios():
                self.demo_scenario_combo.addItem(scenario.display_name, scenario.scenario_id)
            idx = max(0, self.demo_scenario_combo.findData(self.demo_runtime.active_scenario_id))
            self.demo_scenario_combo.setCurrentIndex(idx)
            self.demo_scenario_combo.currentIndexChanged.connect(self._on_demo_scenario_changed)
            self.live_device_combo = QtWidgets.QComboBox()
            self.live_device_combo.currentIndexChanged.connect(self._refresh_capability_summary)
            self._refresh_live_device_inventory()
            self.connect_live_button = QtWidgets.QPushButton('Connect Live Device')
            self.connect_live_button.clicked.connect(self._connect_live_device)
            self.disconnect_live_button = QtWidgets.QPushButton('Disconnect')
            self.disconnect_live_button.clicked.connect(self._disconnect_live_device)
            self.arm_control_button = QtWidgets.QPushButton('Enter Armed Control')
            self.arm_control_button.clicked.connect(lambda: self._set_control_posture('armed_control'))
            self.view_only_button = QtWidgets.QPushButton('Return to View Only')
            self.view_only_button.clicked.connect(lambda: self._set_control_posture('view_only'))
            self.guarded_write_button = QtWidgets.QPushButton('Guarded Write DAC0 → 2.500 V')
            self.guarded_write_button.clicked.connect(self._perform_guarded_write)
            self.session_state_label = QtWidgets.QLabel('connected')
            self.runtime_state_label = QtWidgets.QLabel('USER-DEMO / simulated')
            self.control_posture_label = QtWidgets.QLabel(self.control_posture)
            self.capability_summary_label = QtWidgets.QLabel('Capability summary pending')
            self.capability_summary_label.setWordWrap(True)
            self.capability_reason_label = QtWidgets.QLabel('')
            self.capability_reason_label.setWordWrap(True)
            self.capability_reason_label.setStyleSheet('color: #c2410c;')
            layout.addRow('Demo Scenario', self.demo_scenario_combo)
            layout.addRow('Live Device', self.live_device_combo)
            layout.addRow(self.connect_live_button)
            layout.addRow(self.disconnect_live_button)
            layout.addRow('Session State', self.session_state_label)
            layout.addRow('Runtime', self.runtime_state_label)
            layout.addRow('Capability', self.capability_summary_label)
            layout.addRow('Access Note', self.capability_reason_label)
            layout.addRow('Control Posture', self.control_posture_label)
            layout.addRow(self.arm_control_button)
            layout.addRow(self.view_only_button)
            layout.addRow(self.guarded_write_button)
            return panel

        def _build_signals_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.signal_lens_combo = QtWidgets.QComboBox()
            for lens in self.spec.foundation.signal_lenses:
                self.signal_lens_combo.addItem(lens.display_name, lens.lens_id)
            index = max(0, self.signal_lens_combo.findData(self.selected_lens_id))
            self.signal_lens_combo.setCurrentIndex(index)
            self.signal_lens_combo.currentIndexChanged.connect(self._on_lens_changed)
            self.available_signals_list = QtWidgets.QListWidget()
            self.available_signals_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            add_btn = QtWidgets.QPushButton('Add Selected Trace(s)')
            add_btn.clicked.connect(self._add_selected_signals)
            remove_btn = QtWidgets.QPushButton('Remove Selected Trace')
            remove_btn.clicked.connect(self._remove_selected_trace)
            layout.addWidget(self.signal_lens_combo)
            layout.addWidget(self.available_signals_list, 1)
            layout.addWidget(add_btn)
            layout.addWidget(remove_btn)
            return panel

        def _build_trace_inspector_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.trace_hint_label = QtWidgets.QLabel('Select a legend row to edit its style, axis, markers, and emphasis.')
            self.trace_hint_label.setWordWrap(True)
            layout.addWidget(self.trace_hint_label)
            form = QtWidgets.QFormLayout()
            self.trace_name_label = QtWidgets.QLabel('No trace selected')
            self.trace_color_button = QtWidgets.QPushButton('Choose…')
            self.trace_color_button.clicked.connect(self._choose_trace_color)
            self.trace_width_spin = QtWidgets.QSpinBox(); self.trace_width_spin.setRange(1, 8)
            self.trace_width_spin.valueChanged.connect(self._apply_trace_style_from_controls)
            self.trace_line_combo = QtWidgets.QComboBox(); self.trace_line_combo.addItems(['solid', 'dashed', 'dotted'])
            self.trace_line_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            self.trace_marker_combo = QtWidgets.QComboBox(); self.trace_marker_combo.addItems(['none', 'circle', 'square'])
            self.trace_marker_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            self.trace_marker_size_spin = QtWidgets.QSpinBox(); self.trace_marker_size_spin.setRange(0, 12)
            self.trace_marker_size_spin.valueChanged.connect(self._apply_trace_style_from_controls)
            self.trace_axis_combo = QtWidgets.QComboBox(); self.trace_axis_combo.addItems(['primary', 'secondary'])
            self.trace_axis_combo.setToolTip('Primary axis is active now. Secondary-axis selection is stored as preview-only in this package.')
            self.trace_axis_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            self.trace_glow_checkbox = QtWidgets.QCheckBox('Glow edge')
            self.trace_glow_checkbox.setEnabled(False)
            self.trace_glow_checkbox.setToolTip('Preview-only in this package; line and marker styling are active.')
            self.trace_glow_checkbox.toggled.connect(self._apply_trace_style_from_controls)
            self.trace_blink_combo = QtWidgets.QComboBox(); self.trace_blink_combo.addItems(['off', 'selected', 'critical_only'])
            self.trace_blink_combo.setEnabled(False)
            self.trace_blink_combo.setToolTip('Preview-only in this package; line and marker styling are active.')
            self.trace_blink_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            reset_button = QtWidgets.QPushButton('Reset Trace Style')
            reset_button.clicked.connect(self._reset_active_trace_style)
            form.addRow('Trace', self.trace_name_label)
            form.addRow('Color', self.trace_color_button)
            form.addRow('Line width', self.trace_width_spin)
            form.addRow('Line style', self.trace_line_combo)
            form.addRow('Marker', self.trace_marker_combo)
            form.addRow('Marker size', self.trace_marker_size_spin)
            form.addRow('Axis', self.trace_axis_combo)
            form.addRow(self.trace_glow_checkbox)
            form.addRow('Blink', self.trace_blink_combo)
            form.addRow(reset_button)
            layout.addLayout(form)
            layout.addStretch(1)
            return panel

        def _build_notes_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.note_entry = QtWidgets.QPlainTextEdit()
            self.note_entry.setPlaceholderText('Add a timestamped operator note…')
            self.note_list = QtWidgets.QListWidget()
            add_btn = QtWidgets.QPushButton('Add Note')
            add_btn.clicked.connect(self._add_note)
            layout.addWidget(self.note_entry)
            layout.addWidget(add_btn)
            layout.addWidget(self.note_list, 1)
            return panel

        def _build_diagnostics_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.diagnostics_text = QtWidgets.QPlainTextEdit()
            self.diagnostics_text.setReadOnly(True)
            export_btn = QtWidgets.QPushButton('Export Diagnostics…')
            export_btn.clicked.connect(self._export_diagnostics)
            layout.addWidget(self.diagnostics_text, 1)
            layout.addWidget(export_btn)
            return panel

        def _refresh_signal_inventory(self) -> None:
            self.available_signals_list.clear()
            self.device_explorer.clear()
            self.signal_explorer.clear()
            self.logic_explorer.clear()
            descriptors = tuple(self.runtime.signal_descriptors(lens_id=self.selected_lens_id))
            lens_id = self.signal_lens_combo.currentData() if hasattr(self, 'signal_lens_combo') else self.selected_lens_id
            device_context_key, device_context_label = self._current_device_context()
            self._selected_device_context_key = device_context_key
            self._selected_device_context_label = device_context_label

            device_capability = 'simulated' if self.runtime_mode != 'LIVE' else 'live device pending'
            runtime_label = self.runtime_mode
            live_record = self._selected_capability_record() if self.runtime_mode == 'LIVE' else None
            if live_record is not None:
                device_capability = f"{live_record.capability_mode} / {live_record.read_state} / {live_record.write_state}"
                runtime_label = live_record.limited_access_reason or live_record.hardware_mode
            device_item = QtWidgets.QTreeWidgetItem([device_context_label, device_capability, runtime_label])
            device_item.setData(0, QtCore.Qt.UserRole, {'device_context_key': device_context_key, 'row_id': None})
            self.device_explorer.addTopLevelItem(device_item)

            for descriptor in descriptors:
                signal_id = descriptor.signal_id
                label = self._label_for_signal(signal_id)
                item = QtWidgets.QListWidgetItem(label)
                item.setData(QtCore.Qt.UserRole, descriptor.signal_id)
                self.available_signals_list.addItem(item)
                hardware_name = descriptor.label_for_lens('hardware')
                logical_name = descriptor.label_for_lens('logical')
                capability = 'writable' if getattr(descriptor, 'write_safe', False) else 'readable'
                child_runtime = runtime_label
                if self.runtime_mode == 'LIVE' and live_record is not None:
                    capability = f"{capability} / {live_record.capability_mode}"
                    child_runtime = live_record.limited_access_reason or f"{live_record.read_state} / {live_record.write_state}"
                child = QtWidgets.QTreeWidgetItem([hardware_name, capability, child_runtime])
                child.setData(0, QtCore.Qt.UserRole, {'device_context_key': device_context_key, 'row_id': signal_id})
                device_item.addChild(child)
                signal_item = QtWidgets.QTreeWidgetItem([label, hardware_name, getattr(descriptor, 'source_class', 'signal')])
                signal_item.setData(0, QtCore.Qt.UserRole, signal_id)
                self.signal_explorer.addTopLevelItem(signal_item)
                logic_item = QtWidgets.QTreeWidgetItem([label])
                logic_item.setData(0, QtCore.Qt.UserRole, signal_id)
                self.logic_explorer.addTopLevelItem(logic_item)
            for widget in (self.device_explorer, self.signal_explorer, self.logic_explorer):
                widget.expandAll()
            self.device_explorer.setCurrentItem(device_item)
            if hasattr(self, 'mapping_table'):
                rows = build_mapping_rows(
                    signal_descriptors=descriptors,
                    writable_targets=getattr(self.runtime, 'writable_targets', lambda: ())(),
                    runtime_mode=self.runtime_mode,
                )
                self._mapping_rows = {row.row_id: {
                    'row_id': row.row_id,
                    'direction': row.direction.value,
                    'source_endpoint': row.source_endpoint,
                    'internal_signal_name': row.internal_signal_name,
                    'destination_endpoint': row.destination_endpoint,
                    'status': row.status.value,
                    'capability_label': row.capability_label,
                    'units': row.units,
                    'scale': row.scale,
                    'offset': row.offset,
                    'invert': row.invert,
                    'enabled': row.enabled,
                    'live_capable': row.live_capable,
                    'simulated': row.simulated,
                    'note': row.note,
                    'provenance_label': row.provenance_label,
                } for row in rows}
                self._populate_mapping_table()
                self._populate_mapping_editor_choices()
            self._refresh_device_io_inventory()

        def _refresh_device_io_inventory(self) -> None:
            if not hasattr(self, 'device_io_table'):
                return
            device_context_key = self._selected_device_context_key or self._current_device_context()[0]
            descriptors = tuple(self.runtime.signal_descriptors(lens_id=self.selected_lens_id))
            mapping_rows = build_mapping_rows(
                signal_descriptors=descriptors,
                writable_targets=getattr(self.runtime, 'writable_targets', lambda: ())(),
                runtime_mode=self.runtime_mode,
            )
            self._device_io_rows = [
                {
                    'row_id': row.row_id,
                    'signal_id': row.signal_id,
                    'endpoint_label': row.endpoint_label,
                    'internal_signal_name': row.internal_signal_name,
                    'tag_name': row.tag_name,
                    'direction': row.direction,
                    'source_class': row.source_class,
                    'capability_label': row.capability_label,
                    'authority_state': row.authority_state,
                    'units': row.units,
                    'health_label': row.health_label,
                    'provenance_label': row.provenance_label,
                    'note': row.note,
                }
                for row in build_device_io_rows(
                    device_context_key=device_context_key,
                    signal_descriptors=descriptors,
                    mapping_rows=mapping_rows,
                    authoritative_rows=self._authoritative_binding_rows,
                    tag_names_by_signal=self._tag_names_by_signal,
                    runtime_mode=self.runtime_mode,
                    health_label=self.runtime.connection_state if self.runtime_mode == 'LIVE' else 'simulated',
                )
            ]
            self.device_io_scope_label.setText(f'Device I/O Inspector — {self._selected_device_context_label}')
            self._populate_device_io_table()

        def _populate_device_io_table(self) -> None:
            if not hasattr(self, 'device_io_table'):
                return
            rows = list(self._device_io_rows)
            self.device_io_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row['endpoint_label'],
                    row['internal_signal_name'],
                    row['tag_name'],
                    row['direction'],
                    row['source_class'],
                    row['capability_label'],
                    row['authority_state'],
                    row['units'],
                ]
                for col_index, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setData(QtCore.Qt.UserRole, row['row_id'])
                    self.device_io_table.setItem(row_index, col_index, item)
            self.device_io_table.resizeColumnsToContents()
            if rows:
                self.device_io_table.selectRow(0)
                self._on_device_io_selection_changed()

        def _selected_device_io_row_id(self) -> str | None:
            if not hasattr(self, 'device_io_table'):
                return None
            items = self.device_io_table.selectedItems()
            if not items:
                return None
            return items[0].data(QtCore.Qt.UserRole)

        def _on_device_io_selection_changed(self) -> None:
            row_id = self._selected_device_io_row_id()
            if row_id is None:
                return
            row = next((row for row in self._device_io_rows if row['row_id'] == row_id), None)
            if row is None:
                return
            self.device_io_context_label.setText(self._selected_device_context_label)
            self.device_io_endpoint_label.setText(row['endpoint_label'])
            self.device_io_internal_label.setText(row['internal_signal_name'])
            self.device_io_tag_edit.blockSignals(True)
            self.device_io_tag_edit.setText(row['tag_name'])
            self.device_io_tag_edit.blockSignals(False)
            self.device_io_authority_label.setText(row['authority_state'])
            self.device_io_capability_label.setText(row['capability_label'])
            note_parts = [row['health_label'], row['provenance_label'], row['note']]
            self.device_io_note_label.setText(' | '.join(part for part in note_parts if part))
            if row.get('signal_id'):
                self._set_selected_trace(row['signal_id'])

        def _apply_device_tag_edit(self) -> None:
            row_id = self._selected_device_io_row_id()
            if row_id is None:
                return
            row = next((row for row in self._device_io_rows if row['row_id'] == row_id), None)
            if row is None:
                return
            new_tag = self.device_io_tag_edit.text().strip()
            signal_id = row['signal_id']
            if not signal_id:
                return
            if new_tag:
                self._tag_names_by_signal[signal_id] = new_tag
            else:
                self._tag_names_by_signal.pop(signal_id, None)
            self._trace_name_by_signal.pop(signal_id, None)
            self._save_tag_names()
            self._refresh_signal_inventory()
            self._sync_trace_inspector()
            self.statusBar().showMessage(f'Updated canonical tag: {self._label_for_signal(signal_id)}', 2500)

        def _on_device_explorer_selection_changed(self) -> None:
            item = self.device_explorer.currentItem() if hasattr(self, 'device_explorer') else None
            if item is None:
                return
            payload = item.data(0, QtCore.Qt.UserRole) or {}
            device_context_key = payload.get('device_context_key')
            if device_context_key:
                self._selected_device_context_key = str(device_context_key)
                self._selected_device_context_label = item.text(0) if item.parent() is None else item.parent().text(0)
            row_id = payload.get('row_id')
            self._refresh_device_io_inventory()
            if row_id:
                for row_index, row in enumerate(self._device_io_rows):
                    if row['row_id'] == row_id:
                        self.device_io_table.selectRow(row_index)
                        break

        def _populate_mapping_table(self) -> None:
            if not hasattr(self, 'mapping_table'):
                return
            rows = list(self._mapping_rows.values())
            self.mapping_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row['direction'],
                    row['source_endpoint'],
                    row['internal_signal_name'],
                    row['destination_endpoint'],
                    row['status'],
                    row['units'],
                    'yes' if row['enabled'] else 'no',
                ]
                for col_index, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setData(QtCore.Qt.UserRole, row['row_id'])
                    self.mapping_table.setItem(row_index, col_index, item)
            self.mapping_table.resizeColumnsToContents()

        def _populate_mapping_editor_choices(self) -> None:
            if not hasattr(self, 'mapping_source_combo'):
                return
            self.mapping_source_combo.blockSignals(True)
            self.mapping_destination_combo.blockSignals(True)
            self.mapping_source_combo.clear()
            self.mapping_destination_combo.clear()
            self.mapping_source_combo.addItem('', '')
            self.mapping_destination_combo.addItem('', '')
            descriptors = tuple(self.runtime.signal_descriptors(lens_id=self.selected_lens_id))
            for descriptor in descriptors:
                self.mapping_source_combo.addItem(descriptor.label_for_lens('hardware'), descriptor.label_for_lens('hardware'))
                self.mapping_destination_combo.addItem(descriptor.label_for_lens('hardware'), descriptor.label_for_lens('hardware'))
            for target in getattr(self.runtime, 'writable_targets', lambda: ())():
                label = getattr(target, 'display_name', getattr(target, 'point_id', ''))
                self.mapping_destination_combo.addItem(str(label), str(label))
            self.mapping_source_combo.blockSignals(False)
            self.mapping_destination_combo.blockSignals(False)

        def _selected_mapping_row_id(self) -> str | None:
            if not hasattr(self, 'mapping_table'):
                return None
            items = self.mapping_table.selectedItems()
            if not items:
                return None
            return items[0].data(QtCore.Qt.UserRole)

        def _on_mapping_selection_changed(self) -> None:
            row_id = self._selected_mapping_row_id()
            if row_id is None:
                self.mapping_status_label.setText('No draft selected — backend-applied mappings are not edited here yet')
                return
            row = self._mapping_rows.get(row_id)
            if row is None:
                self.mapping_status_label.setText('Selected mapping missing')
                return
            self.mapping_direction_combo.setCurrentText(str(row['direction']))
            self.mapping_source_combo.setCurrentText(str(row['source_endpoint']))
            self.mapping_internal_name_edit.setText(str(row['internal_signal_name']))
            self.mapping_destination_combo.setCurrentText(str(row['destination_endpoint']))
            self.mapping_scale_spin.setValue(float(row['scale']))
            self.mapping_offset_spin.setValue(float(row['offset']))
            self.mapping_invert_checkbox.setChecked(bool(row['invert']))
            self.mapping_enabled_checkbox.setChecked(bool(row['enabled']))
            self.mapping_note_edit.setPlainText(str(row['note']))
            self.mapping_status_label.setText(f"{row['status']} — {row['capability_label']}")

        def _apply_mapping_edit(self) -> None:
            row_id = self._selected_mapping_row_id() or f"custom::{self.mapping_internal_name_edit.text().strip() or self.mapping_destination_combo.currentText().strip() or self.mapping_source_combo.currentText().strip()}"
            if row_id == 'custom::':
                self.statusBar().showMessage('Mapping edit requires at least one endpoint or signal name', 2500)
                return
            source = self.mapping_source_combo.currentText().strip()
            internal_name = self.mapping_internal_name_edit.text().strip()
            destination = self.mapping_destination_combo.currentText().strip()
            direction = self.mapping_direction_combo.currentText()
            if direction == 'device_input_to_internal_signal' and not source:
                status = 'missing_source'
            elif direction == 'internal_signal_to_device_output' and not destination:
                status = 'missing_destination'
            elif not internal_name:
                status = 'invalid'
            else:
                status = 'mapped'
            self._mapping_rows[row_id] = {
                'row_id': row_id,
                'direction': direction,
                'source_endpoint': source,
                'internal_signal_name': internal_name,
                'destination_endpoint': destination,
                'status': status,
                'capability_label': 'shell_draft_non_authoritative',
                'units': '',
                'scale': float(self.mapping_scale_spin.value()),
                'offset': float(self.mapping_offset_spin.value()),
                'invert': bool(self.mapping_invert_checkbox.isChecked()),
                'enabled': bool(self.mapping_enabled_checkbox.isChecked()),
                'live_capable': self.runtime_mode == 'LIVE',
                'simulated': self.runtime_mode != 'LIVE',
                'note': self.mapping_note_edit.toPlainText().strip(),
                'provenance_label': f'{source} ↔ {internal_name or destination}',
            }
            self._populate_mapping_table()
            self._refresh_system_summary()
            self.statusBar().showMessage(f'Saved shell draft only: {row_id}', 2500)

        def _remove_mapping(self) -> None:
            row_id = self._selected_mapping_row_id()
            if row_id is None:
                return
            row = self._mapping_rows.get(row_id)
            if row is None:
                return
            row['status'] = 'unmapped'
            row['enabled'] = False
            self._populate_mapping_table()
            self._refresh_system_summary()
            self.statusBar().showMessage(f'Marked shell draft unmapped: {row_id}', 2500)

        def _refresh_event_console(self) -> None:
            if not hasattr(self, 'event_table'):
                return
            category_filter = self.event_filter_combo.currentText() if hasattr(self, 'event_filter_combo') else 'All'
            search_text = self.event_search_edit.text().strip().lower() if hasattr(self, 'event_search_edit') else ''
            visible_rows = []
            for row in self._event_rows:
                if category_filter == 'Warnings' and row['severity'] != 'warning':
                    continue
                if category_filter == 'Alarms' and row['category'] != 'Alarms':
                    continue
                if category_filter not in {'All', 'Warnings', 'Alarms'} and row['category'] != category_filter:
                    continue
                haystack = ' '.join(row.values()).lower()
                if search_text and search_text not in haystack:
                    continue
                visible_rows.append(row)
            visible_rows = visible_rows[-200:]
            self.event_table.setRowCount(len(visible_rows))
            for row_index, row in enumerate(visible_rows):
                for col_index, key in enumerate(('timestamp_label', 'severity', 'category', 'message')):
                    self.event_table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(row[key]))
            self.event_table.resizeColumnsToContents()

        def _ensure_default_trace_selection(self) -> None:
            restored_active = self.settings.value('ui/active_traces', '', type=str)
            restored_signal_ids = [item for item in restored_active.split('|') if item]
            if restored_signal_ids:
                for signal_id in restored_signal_ids:
                    self._ensure_trace(signal_id)
            else:
                for descriptor in self.runtime.signal_descriptors()[: min(3, len(self.runtime.signal_descriptors()))]:
                    self._ensure_trace(descriptor.signal_id)
            selected_signal_id = self.settings.value('ui/selected_trace', '', type=str)
            if selected_signal_id and selected_signal_id in self._trace_states:
                self._set_selected_trace(selected_signal_id)
            elif self._trace_states:
                self._set_selected_trace(next(iter(self._trace_states.keys())))

        def _ensure_trace(self, signal_id: str) -> None:
            if signal_id in self._trace_states:
                return
            style = self._initial_style_for_signal(signal_id)
            state = _TraceState(signal_id=signal_id, style=style)
            state.main_item = self.plot_widget.plot([], [], name=self._label_for_signal(signal_id), **self._trace_render_kwargs(style))
            state.overlay_item = self.plot_widget.plot([], [], pen=None)
            state.overlay_item.setZValue(-1)
            self._trace_states[signal_id] = state
            row = QtWidgets.QTreeWidgetItem([self._label_for_signal(signal_id), '—', style.get('axis_assignment', 'primary'), 'normal'])
            row.setFlags(row.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            row.setCheckState(0, QtCore.Qt.Checked)
            row.setData(0, QtCore.Qt.UserRole, signal_id)
            self.legend_tree.addTopLevelItem(row)
            self._legend_rows[signal_id] = row

        def _trace_render_kwargs(self, style: dict[str, Any]) -> dict[str, Any]:
            kwargs: dict[str, Any] = {'pen': _pen_from_style(pg, QtCore, style)}
            marker = {
                'none': None,
                'circle': 'o',
                'square': 's',
            }.get(str(style.get('marker_style', 'none')), None)
            if marker is not None and int(style.get('marker_size', 0) or 0) > 0:
                kwargs.update(
                    {
                        'symbol': marker,
                        'symbolSize': int(style.get('marker_size', 0) or 0),
                        'symbolBrush': style.get('color', '#5dade2'),
                        'symbolPen': style.get('color', '#5dade2'),
                    }
                )
            else:
                kwargs['symbol'] = None
            return kwargs

        def _rerender_trace(self, signal_id: str) -> None:
            state = self._trace_states.get(signal_id)
            if state is None or state.main_item is None or state.overlay_item is None:
                return
            series = self.runtime.trace_series(signal_id)
            if state.visible:
                state.main_item.setData(series.x_values, series.y_values, **self._trace_render_kwargs(state.style))
                state.overlay_item.setData(series.x_values, series.y_values, pen=self._overlay_pen_for_state(state=state, severity='normal'))
            else:
                state.main_item.setData([], [])
                state.overlay_item.setData([], [])

        def _initial_style_for_signal(self, signal_id: str) -> dict[str, Any]:
            saved_styles = self._load_trace_styles()
            if signal_id in saved_styles:
                return dict(saved_styles[signal_id])
            catalog = self.spec.foundation.trace_style_catalog
            if signal_id.endswith('dac_cmd'):
                base = catalog.get('selected')
            else:
                base = catalog.get('base')
            style = asdict(base) if base is not None else {
                'color': '#5dade2',
                'line_width': 2,
                'line_pattern': 'solid',
                'marker_style': 'none',
                'marker_size': 0,
                'opacity_percent': 100,
                'glow_edge': False,
                'selected_highlight': False,
                'blink_mode': 'off',
                'axis_assignment': 'primary',
                'alarm_overlay_policy': 'severity_outline',
                'persistable': True,
            }
            style['selected_highlight'] = False
            return style

        def _load_trace_styles(self) -> dict[str, dict[str, Any]]:
            raw = self.settings.value('ui/trace_styles', '', type=str)
            if not raw:
                return {}
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return {str(key): dict(value) for key, value in payload.items() if isinstance(value, dict)}

        def _save_trace_styles(self) -> None:
            payload = {signal_id: state.style for signal_id, state in self._trace_states.items()}
            self.settings.setValue('ui/trace_styles', json.dumps(payload, sort_keys=True))

        def _render_step(self) -> None:
            snapshot = self.runtime.step()
            selected_snapshot = None
            active_alarm_count = 0
            highest = 'none'
            severity_rank = {'warning': 1, 'high': 2, 'critical': 3}
            for signal_snapshot in snapshot.signal_snapshots:
                severity = signal_snapshot.alarm_severity
                if severity != 'normal':
                    active_alarm_count += 1
                    if severity_rank.get(severity, 0) > severity_rank.get(highest, 0):
                        highest = severity
                state = self._trace_states.get(signal_snapshot.descriptor.signal_id)
                if state is None:
                    continue
                series = self.runtime.trace_series(signal_snapshot.descriptor.signal_id)
                if state.visible:
                    state.main_item.setData(series.x_values, series.y_values, **self._trace_render_kwargs(state.style))
                    overlay_pen = self._overlay_pen_for_state(state=state, severity=severity)
                    state.overlay_item.setData(series.x_values, series.y_values, pen=overlay_pen)
                else:
                    state.main_item.setData([], [])
                    state.overlay_item.setData([], [])
                row = self._legend_rows.get(signal_snapshot.descriptor.signal_id)
                if row is not None:
                    row.setText(0, self._label_for_signal(signal_snapshot.descriptor.signal_id))
                    row.setText(1, f'{signal_snapshot.value:0.3f} {signal_snapshot.descriptor.units or ""}'.strip())
                    row.setText(2, '2nd' if state.style.get('axis_assignment') == 'secondary' else '1st')
                    row.setText(3, severity)
                if signal_snapshot.descriptor.signal_id == self._active_signal_id:
                    selected_snapshot = signal_snapshot
            if self.runtime_mode == 'LIVE':
                self._top_bar_labels['mode'].setText('LIVE')
                self._top_bar_labels['session'].setText(snapshot.connection_state)
                self._top_bar_labels['device'].setText(snapshot.device_label)
                self._top_bar_labels['control'].setText(self.control_posture)
                capability = self._selected_capability_record()
                access_label = 'live device pending' if capability is None else f"{capability.capability_mode} / {capability.read_state} / {capability.write_state}"
                self._top_bar_labels['access'].setText(access_label)
                self._top_bar_labels['alarms'].setText(f'{active_alarm_count} active / highest {highest}')
                self._top_bar_labels['signal'].setText('—' if selected_snapshot is None else self._label_for_signal(selected_snapshot.descriptor.signal_id))
                self._top_bar_labels['freshness'].setText('pending' if selected_snapshot is None else selected_snapshot.freshness_label)
                self.session_state_label.setText(snapshot.connection_state)
                self.runtime_state_label.setText(f'LIVE / {snapshot.runtime_source_label}')
                self.control_posture_label.setText(self.control_posture)
                self.demo_scenario_combo.setEnabled(False)
                self.connect_live_button.setEnabled(True)
                self.disconnect_live_button.setEnabled(snapshot.connection_state == 'connected')
                self.guarded_write_button.setEnabled(True)
                self.arm_control_button.setEnabled(snapshot.connection_state == 'connected')
            else:
                self._top_bar_labels['mode'].setText('USER-DEMO')
                self._top_bar_labels['session'].setText('connected')
                self._top_bar_labels['device'].setText(snapshot.scenario.display_name)
                self._top_bar_labels['control'].setText(self.control_posture)
                self._top_bar_labels['access'].setText('user-demo / simulated')
                self._top_bar_labels['alarms'].setText(f'{active_alarm_count} active / highest {highest}')
                self._top_bar_labels['signal'].setText('—' if selected_snapshot is None else self._label_for_signal(selected_snapshot.descriptor.signal_id))
                self._top_bar_labels['freshness'].setText('simulated' if selected_snapshot is None else selected_snapshot.freshness_label)
                self.session_state_label.setText('connected')
                self.runtime_state_label.setText(f'USER-DEMO / {snapshot.scenario.display_name}')
                self.control_posture_label.setText(self.control_posture)
                self.demo_scenario_combo.setEnabled(True)
                self.connect_live_button.setEnabled(True)
                self.disconnect_live_button.setEnabled(False)
                self.guarded_write_button.setEnabled(True)
                self.arm_control_button.setEnabled(True)
            self.bottom_log.setPlainText('\n'.join(snapshot.event_log))
            self._event_rows = [
                {
                    'timestamp_label': row.timestamp_label,
                    'severity': row.severity,
                    'category': row.category,
                    'message': row.message,
                }
                for row in derive_event_console_rows(snapshot.event_log, elapsed_seconds=snapshot.elapsed_seconds)
            ]
            self._refresh_event_console()
            if selected_snapshot is not None:
                self.active_signal_label.setText(self._label_for_signal(selected_snapshot.descriptor.signal_id))
                self.active_value_label.setText(f'{selected_snapshot.value:0.3f} {selected_snapshot.descriptor.units or ""}'.strip())
                provenance = getattr(selected_snapshot, 'runtime_source_label', 'demo')
                self.active_meta_label.setText(
                    f'Quality: {selected_snapshot.quality_label} | Freshness: {selected_snapshot.freshness_label} | Alarm: {selected_snapshot.alarm_severity} | Runtime: {provenance}'
                )
            else:
                self.active_signal_label.setText('No active signal')
                self.active_value_label.setText('—')
                self.active_meta_label.setText('No active signal bound')
            self._refresh_top_bar_semantics()
            self._render_pip_overlay(snapshot)
            self._refresh_diagnostics(snapshot)
            self._refresh_session_review(snapshot)
            self._refresh_logic_watch(snapshot)
            self._refresh_system_summary()


        def _overlay_pen_for_state(self, *, state: _TraceState, severity: str) -> Any:
            if severity == 'critical':
                return _pen_from_style(pg, QtCore, state.style, color_override='#c0392b', width_offset=4)
            if severity == 'high':
                return _pen_from_style(pg, QtCore, state.style, color_override='#e67e22', width_offset=3)
            if severity == 'warning':
                return _pen_from_style(pg, QtCore, state.style, color_override='#f1c40f', width_offset=2)
            if state.selected:
                return _pen_from_style(pg, QtCore, state.style, color_override='#2c3e50', width_offset=2)
            return None

        def _label_for_signal(self, signal_id: str) -> str:
            if signal_id in self._tag_names_by_signal and self._tag_names_by_signal[signal_id].strip():
                label = self._tag_names_by_signal[signal_id].strip()
                self._trace_name_by_signal[signal_id] = label
                return label
            lens_id = self.signal_lens_combo.currentData() if hasattr(self, 'signal_lens_combo') else self.selected_lens_id
            for descriptor in self.runtime.signal_descriptors(lens_id=lens_id):
                if descriptor.signal_id == signal_id:
                    label = descriptor.label_for_lens(lens_id)
                    self._trace_name_by_signal[signal_id] = label
                    return label
            return self._trace_name_by_signal.get(signal_id, signal_id)

        def _set_selected_trace(self, signal_id: str) -> None:
            self._active_signal_id = signal_id
            for candidate_id, state in self._trace_states.items():
                state.selected = candidate_id == signal_id
                state.style['selected_highlight'] = state.selected
            row = self._legend_rows.get(signal_id)
            if row is not None:
                self.legend_tree.setCurrentItem(row)
            self._sync_trace_inspector()
            self.settings.setValue('ui/selected_trace', signal_id)

        def _sync_trace_inspector(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None or signal_id not in self._trace_states:
                self.trace_name_label.setText('No trace selected')
                return
            state = self._trace_states[signal_id]
            self.trace_name_label.setText(self._label_for_signal(signal_id))
            self.trace_color_button.setText(state.style.get('color', '#5dade2'))
            self.trace_width_spin.blockSignals(True); self.trace_width_spin.setValue(int(state.style.get('line_width', 2))); self.trace_width_spin.blockSignals(False)
            self.trace_line_combo.blockSignals(True); self.trace_line_combo.setCurrentText(state.style.get('line_pattern', 'solid')); self.trace_line_combo.blockSignals(False)
            self.trace_marker_combo.blockSignals(True); self.trace_marker_combo.setCurrentText(state.style.get('marker_style', 'none')); self.trace_marker_combo.blockSignals(False)
            self.trace_marker_size_spin.blockSignals(True); self.trace_marker_size_spin.setValue(int(state.style.get('marker_size', 0))); self.trace_marker_size_spin.blockSignals(False)
            self.trace_axis_combo.blockSignals(True); self.trace_axis_combo.setCurrentText(state.style.get('axis_assignment', 'primary')); self.trace_axis_combo.blockSignals(False)
            self.trace_glow_checkbox.blockSignals(True); self.trace_glow_checkbox.setChecked(bool(state.style.get('glow_edge', False))); self.trace_glow_checkbox.blockSignals(False)
            self.trace_blink_combo.blockSignals(True); self.trace_blink_combo.setCurrentText(state.style.get('blink_mode', 'off')); self.trace_blink_combo.blockSignals(False)

        def _apply_trace_style_from_controls(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None or signal_id not in self._trace_states:
                return
            state = self._trace_states[signal_id]
            state.style.update(
                {
                    'color': self.trace_color_button.text(),
                    'line_width': int(self.trace_width_spin.value()),
                    'line_pattern': self.trace_line_combo.currentText(),
                    'marker_style': self.trace_marker_combo.currentText(),
                    'marker_size': int(self.trace_marker_size_spin.value()),
                    'axis_assignment': self.trace_axis_combo.currentText(),
                    'glow_edge': self.trace_glow_checkbox.isChecked(),
                    'blink_mode': self.trace_blink_combo.currentText(),
                }
            )
            row = self._legend_rows.get(signal_id)
            if row is not None:
                row.setText(2, '2nd' if state.style.get('axis_assignment') == 'secondary' else '1st')
            if state.style.get('axis_assignment') == 'secondary':
                self.statusBar().showMessage('Secondary axis is still preview-only; line and marker styling updates are live.', 3500)
            self._rerender_trace(signal_id)
            self._save_trace_styles()


        def _reset_active_trace_style(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None:
                return
            self._trace_states[signal_id].style = self._initial_style_for_signal(signal_id)
            self._sync_trace_inspector()
            self._rerender_trace(signal_id)
            self._save_trace_styles()

        def _choose_trace_color(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None or signal_id not in self._trace_states:
                return
            color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._trace_states[signal_id].style.get('color', '#5dade2')), self)
            if not color.isValid():
                return
            self.trace_color_button.setText(color.name())
            self._apply_trace_style_from_controls()

        def _on_lens_changed(self) -> None:
            self.selected_lens_id = self.signal_lens_combo.currentData()
            self.settings.setValue('ui/selected_lens_id', self.selected_lens_id)
            self._refresh_signal_inventory()
            for row in self._legend_rows.values():
                signal_id = row.data(0, QtCore.Qt.UserRole)
                row.setText(0, self._label_for_signal(signal_id))

        def _add_selected_signals(self) -> None:
            for item in self.available_signals_list.selectedItems():
                signal_id = item.data(QtCore.Qt.UserRole)
                self._ensure_trace(signal_id)
            if self.available_signals_list.selectedItems():
                self._set_selected_trace(self.available_signals_list.selectedItems()[0].data(QtCore.Qt.UserRole))

        def _remove_selected_trace(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None:
                return
            state = self._trace_states.pop(signal_id, None)
            if state is None:
                return
            self.plot_widget.removeItem(state.main_item)
            self.plot_widget.removeItem(state.overlay_item)
            row = self._legend_rows.pop(signal_id, None)
            if row is not None:
                index = self.legend_tree.indexOfTopLevelItem(row)
                if index >= 0:
                    self.legend_tree.takeTopLevelItem(index)
            self._active_signal_id = None
            if self._trace_states:
                self._set_selected_trace(next(iter(self._trace_states.keys())))
            self._save_settings()

        def _on_legend_selection_changed(self) -> None:
            item = self.legend_tree.currentItem()
            if item is None:
                return
            signal_id = item.data(0, QtCore.Qt.UserRole)
            self._set_selected_trace(signal_id)

        def _on_legend_item_changed(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
            if column != 0:
                return
            signal_id = item.data(0, QtCore.Qt.UserRole)
            state = self._trace_states.get(signal_id)
            if state is None:
                return
            state.visible = item.checkState(0) == QtCore.Qt.Checked
            self._save_settings()

        def _add_note(self) -> None:
            text = self.note_entry.toPlainText().strip()
            if not text:
                return
            entry = f't+{self.runtime.snapshot().elapsed_seconds:0.1f}s — {text}'
            self._notes.append(entry)
            self.note_list.addItem(entry)
            self.note_entry.clear()
            self._refresh_session_review(self.runtime.snapshot())
            self._refresh_system_summary()

        def _review_detail_text(self, item_text: str) -> str:
            snapshot = self.runtime.snapshot()
            scenario_or_device = snapshot.scenario.display_name if self.runtime_mode != 'LIVE' else snapshot.device_label
            return '\n'.join(
                [
                    f'Review Item: {item_text}',
                    f'Runtime: {self.runtime_mode}',
                    f'Context: {scenario_or_device}',
                    f'Elapsed: {snapshot.elapsed_seconds:0.2f} s',
                    f'Notes: {len(self._notes)}',
                    f'Active traces: {len(self._trace_states)}',
                ] + list(snapshot.event_log[-6:])
            )


        def _refresh_session_review(self, snapshot: Any) -> None:
            current = self.session_review_list.currentItem().text() if self.session_review_list.currentItem() else 'Current demo session'
            self.session_review_detail.setPlainText(self._review_detail_text(current))

        def _refresh_diagnostics(self, snapshot: Any) -> None:
            capability = self._selected_capability_record()
            payload = {
                'runtime_mode': self.runtime_mode,
                'scenario_or_device': snapshot.scenario.display_name if self.runtime_mode != 'LIVE' else snapshot.device_label,
                'connection_state': 'connected' if self.runtime_mode != 'LIVE' else snapshot.connection_state,
                'signal_count': len(snapshot.signal_snapshots),
                'active_trace_count': len(self._trace_states),
                'selected_lens_id': self.selected_lens_id,
                'selected_trace_id': self._active_signal_id,
                'active_workspace': self.selected_workspace_id,
                'graph_mode': self._graph_presentation,
                'autosave_enabled': self.autosave_enabled,
                'control_posture': self.control_posture,
                'outer_splitter_sizes': list(self.outer_splitter.sizes()),
                'center_splitter_sizes': list(self.center_splitter.sizes()),
                'window_geometry': serialize_rect(self._qt_rect_to_policy_rect(self.geometry())),
                'pip_rect': None if self._pip_rect is None else serialize_rect(self._pip_rect),
                'menu_bar': [menu.label for menu in self.spec.menus],
                'notes': len(self._notes),
                'selected_device_capability': None if capability is None else {
                    'device_key': capability.device_key,
                    'capability_mode': capability.capability_mode,
                    'identity_state': capability.identity_state,
                    'read_state': capability.read_state,
                    'write_state': capability.write_state,
                    'limited_access_reason': capability.limited_access_reason,
                },
                'live_runtime_inventory': self.live_runtime.inventory(),
                'guarded_action': self._last_guard_decision if isinstance(self._last_guard_decision, dict) else None if self._last_guard_decision is None else {
                    'allowed': self._last_guard_decision.allowed,
                    'reason': self._last_guard_decision.reason,
                    'target_class': self._last_guard_decision.target_class,
                    'point_id': self._last_guard_decision.point_id,
                    'request_value': self._last_guard_decision.request_value,
                    'runtime_mode': self._last_guard_decision.runtime_mode,
                    'posture': self._last_guard_decision.posture,
                },
            }
            self.diagnostics_text.setPlainText(json.dumps(payload, indent=2, sort_keys=True))


        def _default_logic_nodes(self) -> list[dict[str, Any]]:
            return [
                {'node_id': 'logic-source-1', 'type': 'Source', 'label': 'Selected Signal Source', 'source_signal_id': ''},
                {'node_id': 'logic-math-1', 'type': 'Math', 'label': 'Scale + Offset', 'scale': 1.0, 'offset': 0.0},
                {'node_id': 'logic-comparator-1', 'type': 'Comparator', 'label': '> Threshold', 'operator': '>', 'threshold': 2.0},
                {'node_id': 'logic-sink-1', 'type': 'Sink', 'label': 'Draft Internal Variable', 'target': 'draft_internal_variable'},
            ]

        def _reset_logic_nodes(self) -> None:
            self._logic_nodes = self._default_logic_nodes()
            self._build_logic_demo_scene()
            self._refresh_logic_watch(self.runtime.snapshot())

        def _add_logic_node(self, node_type: str) -> None:
            node_type = str(node_type or 'Source')
            next_index = len(self._logic_nodes) + 1
            node = {'node_id': f'logic-{node_type.lower()}-{next_index}', 'type': node_type, 'label': node_type}
            if node_type == 'Source':
                node['source_signal_id'] = self._active_signal_id or ''
                node['label'] = 'Tagged / Selected Source'
            elif node_type == 'Filter':
                node.update({'label': 'Low-pass Filter', 'filter_kind': 'low_pass', 'alpha': 0.45})
            elif node_type == 'Math':
                node.update({'label': 'Scale + Offset', 'scale': 1.0, 'offset': 0.0})
            elif node_type == 'Comparator':
                node.update({'label': '> Threshold', 'operator': '>', 'threshold': 2.0})
            elif node_type == 'Sink':
                node.update({'label': 'Draft Sink', 'target': f'draft_sink_{next_index}'})
            self._logic_nodes.append(node)
            self._build_logic_demo_scene()
            self._refresh_logic_watch(self.runtime.snapshot())
            self.statusBar().showMessage(f'Added draft logic node: {node_type}', 2500)

        def _remove_last_logic_node(self) -> None:
            if not self._logic_nodes:
                return
            removed = self._logic_nodes.pop()
            self._build_logic_demo_scene()
            self._refresh_logic_watch(self.runtime.snapshot())
            self.statusBar().showMessage(f"Removed draft logic node: {removed.get('label', removed.get('type', 'node'))}", 2500)

        def _evaluate_logic_nodes(self, snapshot: Any) -> list[dict[str, Any]]:
            signal_map = {item.descriptor.signal_id: item for item in snapshot.signal_snapshots}
            if not self._logic_nodes:
                self._logic_nodes = self._default_logic_nodes()
            rows: list[dict[str, Any]] = []
            current_value = 0.0
            current_label = 'unset'
            for node in self._logic_nodes:
                node_type = str(node.get('type', 'Source'))
                if node_type == 'Source':
                    signal_id = str(node.get('source_signal_id') or self._active_signal_id or (next(iter(signal_map)) if signal_map else ''))
                    snapshot_row = signal_map.get(signal_id)
                    current_value = 0.0 if snapshot_row is None else float(snapshot_row.value)
                    current_label = self._label_for_signal(signal_id) if signal_id else 'No signal selected'
                    node['source_signal_id'] = signal_id
                    output_text = f'{current_value:0.3f}'
                    detail = current_label
                elif node_type == 'Filter':
                    filter_kind = str(node.get('filter_kind', 'low_pass'))
                    alpha = float(node.get('alpha', 0.45))
                    if filter_kind == 'low_pass':
                        previous = float(self._logic_last_outputs.get(node['node_id'], current_value))
                        current_value = previous + alpha * (current_value - previous)
                        detail = f'low_pass α={alpha:0.2f}'
                    else:
                        detail = filter_kind
                    output_text = f'{current_value:0.3f}'
                elif node_type == 'Math':
                    scale = float(node.get('scale', 1.0))
                    offset = float(node.get('offset', 0.0))
                    current_value = current_value * scale + offset
                    detail = f'scale={scale:0.2f}, offset={offset:0.2f}'
                    output_text = f'{current_value:0.3f}'
                elif node_type == 'Comparator':
                    operator = str(node.get('operator', '>'))
                    threshold = float(node.get('threshold', 2.0))
                    if operator == '<':
                        current_value = 1.0 if current_value < threshold else 0.0
                    elif operator == '==':
                        current_value = 1.0 if abs(current_value - threshold) <= 1e-9 else 0.0
                    else:
                        current_value = 1.0 if current_value > threshold else 0.0
                    detail = f'{operator} {threshold:0.2f}'
                    output_text = 'true' if current_value > 0.5 else 'false'
                elif node_type == 'Sink':
                    target = str(node.get('target', 'draft_sink'))
                    detail = f'draft target: {target}'
                    output_text = f'{current_value:0.3f}'
                else:
                    detail = 'passthrough'
                    output_text = f'{current_value:0.3f}'
                self._logic_last_outputs[node['node_id']] = current_value
                rows.append({'label': str(node.get('label', node_type)), 'type': node_type, 'detail': detail, 'output': output_text})
            return rows

        def _refresh_logic_watch(self, snapshot: Any) -> None:
            rows = self._evaluate_logic_nodes(snapshot)
            self.logic_inspector.clear()
            lines = [
                f'Logic draft state: simulated ({self.runtime_mode})',
                'Authority: draft / simulated only — not yet applied to runtime control',
            ]
            for row in rows:
                lines.append(f"{row['type']}: {row['label']} | {row['detail']} | output {row['output']}")
                parent = QtWidgets.QTreeWidgetItem(self.logic_inspector, [row['label'], row['output']])
                QtWidgets.QTreeWidgetItem(parent, ['Type', row['type']])
                QtWidgets.QTreeWidgetItem(parent, ['Detail', row['detail']])
            self.logic_inspector.expandAll()
            self.logic_watch.setPlainText('\n'.join(lines))

        def _build_logic_demo_scene(self) -> None:
            if not self._logic_nodes:
                self._logic_nodes = self._default_logic_nodes()
            self.logic_scene.clear()
            x = 20
            y = 40
            box_w = 180
            box_h = 92
            gap = 48
            for node in self._logic_nodes:
                label = str(node.get('label', node.get('type', 'Node')))
                node_type = str(node.get('type', 'Node'))
                detail = ''
                if node_type == 'Source':
                    detail = self._label_for_signal(str(node.get('source_signal_id') or self._active_signal_id or ''))
                elif node_type == 'Math':
                    detail = f"scale {float(node.get('scale', 1.0)):0.2f} / offset {float(node.get('offset', 0.0)):0.2f}"
                elif node_type == 'Comparator':
                    detail = f"{node.get('operator', '>')} {float(node.get('threshold', 2.0)):0.2f}"
                elif node_type == 'Filter':
                    detail = f"{node.get('filter_kind', 'low_pass')} α={float(node.get('alpha', 0.45)):0.2f}"
                elif node_type == 'Sink':
                    detail = str(node.get('target', 'draft_sink'))
                rect = self.logic_scene.addRect(x, y, box_w, box_h, pen=QtGui.QPen(QtGui.QColor('#6ea8fe'), 2), brush=QtGui.QBrush(QtGui.QColor('#1f2933')))
                title = self.logic_scene.addText(label)
                title.setDefaultTextColor(QtGui.QColor('#f5f7fa'))
                title.setPos(x + 12, y + 12)
                subtitle = self.logic_scene.addText(f'{node_type} — {detail}')
                subtitle.setDefaultTextColor(QtGui.QColor('#cbd5e1'))
                subtitle.setPos(x + 12, y + 46)
                _ = rect
                if x > 20:
                    self.logic_scene.addLine(x - gap + 16, y + box_h / 2, x, y + box_h / 2, pen=QtGui.QPen(QtGui.QColor('#7f8c8d'), 2, QtCore.Qt.DashLine))
                x += box_w + gap

        def resizeEvent(self, event: Any) -> None:
            super().resizeEvent(event)
            parent = self.parentWidget()
            if parent is not None and hasattr(parent.window(), '_clamp_and_commit_pip_geometry'):
                parent.window()._clamp_and_commit_pip_geometry()

    class OperatorShellWindow(QtWidgets.QMainWindow):
        def __init__(self, *, spec: VisibleOperatorShellSpec, diagnostics_path: str | None = None, bench_mode: bool = False) -> None:
            super().__init__()
            self.spec = spec
            self.demo_runtime = DemoRuntimeEngine(scenario_id=initial_scenario_id)
            self.live_runtime = LiveRuntimeEngine()
            self.control_posture = 'view_only'
            self._last_guard_decision = None
            self.settings = QtCore.QSettings(_GUI_SETTINGS_ORG, _GUI_SETTINGS_APP)
            env_diagnostics_path = os.environ.get('UNIVERSALDAQ_SHELL_DIAGNOSTICS_PATH')
            self._diagnostics_path = None if not (diagnostics_path or env_diagnostics_path) else Path(diagnostics_path or env_diagnostics_path).expanduser().resolve()
            self._bench_mode = bool(bench_mode or os.environ.get('UNIVERSALDAQ_BENCH_MODE') == '1')
            self._bench_runbook_path = os.environ.get('UNIVERSALDAQ_BENCH_RUNBOOK_PATH')
            self.runtime_mode = self.settings.value('runtime/mode', 'USER-DEMO', type=str)
            self.runtime = self.demo_runtime if self.runtime_mode != 'LIVE' else self.live_runtime
            self.autosave_enabled = self.settings.value('ui/autosave_enabled', spec.foundation.autosave_preferences.enabled, type=bool)
            self.autosave_interval_seconds = self.settings.value('ui/autosave_interval_seconds', spec.foundation.autosave_preferences.interval_seconds, type=int)
            self.selected_lens_id = self.settings.value('ui/selected_lens_id', 'logical', type=str)
            self.selected_workspace_id = self.settings.value('ui/selected_workspace', spec.foundation.default_workspace, type=str)
            self._notes: list[str] = []
            self._trace_states: dict[str, _TraceState] = {}
            self._active_signal_id: str | None = None
            self._legend_rows: dict[str, QtWidgets.QTreeWidgetItem] = {}
            self._trace_name_by_signal: dict[str, str] = {}
            self._tag_names_by_signal = self._load_tag_names()
            self._selected_device_context_key: str | None = None
            self._selected_device_context_label: str = 'No device selected'
            self._device_io_rows: list[dict[str, Any]] = []
            self._logic_nodes: list[dict[str, Any]] = []
            self._logic_last_outputs: dict[str, float] = {}
            self._logic_nodes = self._default_logic_nodes()
            self._graph_setups = self._load_graph_setups()
            self._saved_views = ShellViewCatalog.from_json(self.settings.value('ui/saved_views_json', '', type=str))
            self._mapping_rows: dict[str, dict[str, Any]] = {}
            self._event_rows: list[dict[str, str]] = []
            self._ui_built = False
            self._layout_schema_version = LAYOUT_SCHEMA_VERSION
            self._graph_presentation_override: str | None = None
            self._graph_presentation = default_graph_presentation_for_workspace(self.selected_workspace_id)
            self._pip_rect: Rect | None = None
            self._live_device_records_by_key: dict[str, Any] = {}
            self._authoritative_binding_rows: tuple[dict[str, Any], ...] = ()
            self._authoritative_binding_status = 'unavailable'
            self.setWindowTitle(f'{spec.shell_title} — Visible Operator Shell')
            self._build_shell()
            self._restore_settings()
            self._refresh_signal_inventory()
            self._ensure_default_trace_selection()
            self._apply_workspace_selection(self.selected_workspace_id)
            self._build_logic_demo_scene()
            self._ui_built = True
            if self._bench_mode:
                self.statusBar().showMessage('Desktop bench mode active — diagnostics will be written on exit', 5000)
            self._render_step()
            self._start_timers()

        def _build_shell(self) -> None:
            self._build_menus()
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)
            root_layout = QtWidgets.QVBoxLayout(central)
            root_layout.setContentsMargins(6, 6, 6, 6)
            root_layout.setSpacing(6)
            self.top_bar = self._build_top_bar()
            root_layout.addWidget(self.top_bar)
            self.workspace_tabs = QtWidgets.QTabWidget()
            self.workspace_host = QtWidgets.QFrame()
            self.workspace_host.setObjectName('workspaceHost')
            workspace_host_layout = QtWidgets.QVBoxLayout(self.workspace_host)
            workspace_host_layout.setContentsMargins(0, 0, 0, 0)
            workspace_host_layout.setSpacing(0)
            workspace_host_layout.addWidget(self.workspace_tabs, 1)
            self._build_operate_workspace()
            self._build_logic_workspace()
            self._build_session_review_workspace()
            self._build_system_workspace()
            self.workspace_tabs.currentChanged.connect(self._on_workspace_tab_changed)
            self._build_right_control_dock()
            self._build_bottom_log_dock()
            self._build_explorer_dock()
            self.center_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
            self.center_splitter.setChildrenCollapsible(False)
            self.center_splitter.addWidget(self.workspace_host)
            self.center_splitter.addWidget(self.bottom_dock)
            self.center_splitter.setStretchFactor(0, 1)
            self.center_splitter.setStretchFactor(1, 0)
            self.outer_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            self.outer_splitter.setChildrenCollapsible(False)
            self.outer_splitter.addWidget(self.explorer_dock)
            self.outer_splitter.addWidget(self.center_splitter)
            self.outer_splitter.addWidget(self.control_dock)
            self.outer_splitter.setStretchFactor(0, 0)
            self.outer_splitter.setStretchFactor(1, 1)
            self.outer_splitter.setStretchFactor(2, 0)
            root_layout.addWidget(self.outer_splitter, 1)
            self.pip_overlay = PipOverlayWidget(parent=self.workspace_host, on_expand=self._toggle_graph_primary_overlay, on_hide=self._hide_graph_overlay)
            self.pip_overlay.hide()
            self._reset_panel_sizes()
            self.statusBar().showMessage('Ready')

        def _mode_badge(self) -> str:
            return 'USER-DEMO' if self.runtime_mode == 'USER-DEMO' else 'LIVE'

        def _switch_runtime_mode(self, mode: str) -> None:
            self.runtime_mode = mode
            self.runtime = self.demo_runtime if mode != 'LIVE' else self.live_runtime
            self.control_posture = 'view_only' if mode == 'LIVE' else self.control_posture
            if hasattr(self, 'runtime_state_label'):
                self.runtime_state_label.setText(f'{self._mode_badge()} / {getattr(self.runtime, "runtime_source_label", "simulated")}')
            self.settings.setValue('runtime/mode', self.runtime_mode)
            self._sync_mode_menu_checks()
            self._refresh_live_device_inventory()
            self._clear_plot_state()
            self._refresh_signal_inventory()
            self._ensure_default_trace_selection()
            self._render_step()

        def _sync_mode_menu_checks(self) -> None:
            for action_id, mode in (('mode_user_demo', 'USER-DEMO'), ('mode_live', 'LIVE')):
                action = self._menu_actions.get(action_id)
                if action is not None:
                    action.setChecked(self.runtime_mode == mode)

        def _clear_plot_state(self) -> None:
            for item in list(self._trace_states.values()):
                self.plot_widget.removeItem(item.main_item)
                self.plot_widget.removeItem(item.overlay_item)
            self._trace_states.clear()
            self._legend_rows.clear()
            self.legend_tree.clear()
            if hasattr(self, 'pip_overlay'):
                self.pip_overlay.plot_widget.clear()
            self._active_signal_id = None

        def _refresh_live_device_inventory(self) -> None:
            if not hasattr(self, 'live_device_combo'):
                return
            self.live_device_combo.blockSignals(True)
            self.live_device_combo.clear()
            self._live_device_records_by_key = {}
            for device in self.live_runtime.available_devices():
                self._live_device_records_by_key[device.device_key] = device
                label = f'{device.display_name} [{device.hardware_mode} / {device.capability_mode}]'
                self.live_device_combo.addItem(label, device.device_key)
            self.live_device_combo.blockSignals(False)
            self._refresh_capability_summary()

        def _selected_live_device_key(self) -> str | None:
            if not hasattr(self, 'live_device_combo'):
                return None
            return self.live_device_combo.currentData()

        def _selected_capability_record(self):
            device_key = self._selected_live_device_key()
            if not device_key:
                return None
            return getattr(self, '_live_device_records_by_key', {}).get(device_key)

        def _refresh_capability_summary(self) -> None:
            if not hasattr(self, 'capability_summary_label'):
                return
            record = self._selected_capability_record()
            if record is None:
                if getattr(self, 'live_device_combo', None) is not None and self.live_device_combo.count() > 0:
                    summary = 'Select a live device to inspect capability state'
                    reason = 'Capability state is available after you choose a discovered device.'
                else:
                    summary = 'No live devices discovered yet'
                    reason = 'Generic discovery remains active. If a support pack is absent, limited capability reporting may still appear when a device is detected.'
            else:
                summary = f"{record.capability_mode} / {record.identity_state} / {record.read_state} / {record.write_state}"
                reason = record.limited_access_reason or 'No access limitation reported for the selected device.'
            self.capability_summary_label.setText(summary)
            self.capability_reason_label.setText(reason)

        def _build_menus(self) -> None:
            menu_bar = self.menuBar()
            self._menu_actions: dict[str, QtGui.QAction] = {}
            for menu_spec in self.spec.menus:
                menu = menu_bar.addMenu(menu_spec.label)
                for action_spec in menu_spec.actions:
                    action = QtGui.QAction(action_spec.label, self)
                    action.setCheckable(action_spec.checkable)
                    if action_spec.checkable:
                        action.setChecked(action_spec.checked)
                    action.setEnabled(action_spec.enabled)
                    if action_spec.tooltip:
                        action.setToolTip(action_spec.tooltip)
                    self._menu_actions[action_spec.action_id] = action
                    menu.addAction(action)
            self._menu_actions['file_exit'].triggered.connect(self.close)
            self._menu_actions['file_save_graph_setup'].triggered.connect(self._save_graph_setup_interactive)
            self._menu_actions['file_load_graph_setup'].triggered.connect(self._load_graph_setup_interactive)
            self._menu_actions['file_export_session_report'].triggered.connect(self._export_lightweight_report)
            self._menu_actions['view_restore_default_layout'].triggered.connect(self._restore_default_layout)
            self._menu_actions['view_save_current_view'].triggered.connect(self._save_current_view_interactive)
            self._menu_actions['view_manage_saved_views'].triggered.connect(self._manage_saved_views_interactive)
            self._menu_actions['view_reset_panel_sizes'].triggered.connect(self._reset_panel_sizes)
            if 'view_reset_layout_cache' in self._menu_actions:
                self._menu_actions['view_reset_layout_cache'].triggered.connect(self._reset_layout_cache)
            self._menu_actions['view_toggle_device_explorer'].triggered.connect(self._toggle_device_explorer_tab)
            self._menu_actions['view_toggle_signal_explorer'].triggered.connect(self._toggle_signal_explorer_tab)
            self._menu_actions['view_toggle_control_dock'].triggered.connect(self._toggle_control_dock)
            self._menu_actions['view_toggle_bottom_log'].triggered.connect(self._toggle_bottom_dock)
            self._menu_actions['view_toggle_trace_inspector'].triggered.connect(self._toggle_trace_inspector_tab)
            self._menu_actions['view_toggle_notes'].triggered.connect(self._toggle_notes_tab)
            self._menu_actions['settings_preferences'].triggered.connect(self._open_preferences)
            self._menu_actions['settings_autosave_toggle'].triggered.connect(self._toggle_autosave_from_menu)
            self._menu_actions['help_export_diagnostics'].triggered.connect(self._export_diagnostics)
            self._menu_actions['help_about'].triggered.connect(self._show_about)
            self._menu_actions['help_user_demo_guide'].triggered.connect(self._show_demo_guide)
            if 'testing_run_smoke' in self._menu_actions:
                self._menu_actions['testing_run_smoke'].triggered.connect(lambda: self._run_testing_action('smoke'))
            if 'testing_run_sandbox_demo' in self._menu_actions:
                self._menu_actions['testing_run_sandbox_demo'].triggered.connect(lambda: self._run_testing_action('sandbox_demo'))
            if 'testing_run_apply_rollback' in self._menu_actions:
                self._menu_actions['testing_run_apply_rollback'].triggered.connect(lambda: self._run_testing_action('apply_rollback'))
            if 'testing_run_diff_report' in self._menu_actions:
                self._menu_actions['testing_run_diff_report'].triggered.connect(lambda: self._run_testing_action('diff_report'))
            if 'testing_run_shell_wiring_audit' in self._menu_actions:
                self._menu_actions['testing_run_shell_wiring_audit'].triggered.connect(lambda: self._run_testing_action('visible_shell_wiring_audit'))
            if 'testing_export_bundle' in self._menu_actions:
                self._menu_actions['testing_export_bundle'].triggered.connect(lambda: self._run_testing_action('diagnostic_bundle'))
            if 'testing_open_manual_checklist' in self._menu_actions:
                self._menu_actions['testing_open_manual_checklist'].triggered.connect(self._open_manual_test_checklist)
            if 'testing_open_report_folder' in self._menu_actions:
                self._menu_actions['testing_open_report_folder'].triggered.connect(self._open_latest_test_report_folder)
            self._menu_actions['mode_user_demo'].triggered.connect(self._ensure_demo_mode)
            self._menu_actions['mode_live'].triggered.connect(self._ensure_live_mode)
            for workspace in self.spec.workspaces:
                action = self._menu_actions.get(f'workspace_{workspace.workspace_id}')
                if action is not None:
                    action.triggered.connect(lambda checked=False, ws=workspace.workspace_id: self._apply_workspace_selection(ws))

        def _testing_package_root(self) -> Path:
            from universaldaq.testing import package_root_from
            return package_root_from(Path.cwd())

        def _run_testing_action(self, action_id: str) -> None:
            from universaldaq.testing import (
                export_diagnostic_bundle,
                run_apply_rollback_test,
                run_diff_report_test,
                run_mapping_sandbox_demo,
                run_smoke_test,
                run_visible_shell_wiring_audit,
            )
            runners = {
                'smoke': run_smoke_test,
                'sandbox_demo': run_mapping_sandbox_demo,
                'apply_rollback': run_apply_rollback_test,
                'diff_report': run_diff_report_test,
                'visible_shell_wiring_audit': run_visible_shell_wiring_audit,
                'diagnostic_bundle': export_diagnostic_bundle,
            }
            runner = runners.get(action_id)
            if runner is None:
                QtWidgets.QMessageBox.warning(self, 'Testing', f'Unknown testing action: {action_id}')
                return
            self.statusBar().showMessage(f'Running testing action: {action_id}…')
            try:
                result = runner(package_root=self._testing_package_root())
            except Exception as exc:  # pragma: no cover - GUI defensive path
                self.statusBar().showMessage(f'Testing action failed: {exc}', 10000)
                QtWidgets.QMessageBox.critical(self, 'Testing action failed', str(exc))
                return
            level = QtWidgets.QMessageBox.Information if result.passed else QtWidgets.QMessageBox.Warning
            message = QtWidgets.QMessageBox(level, 'Testing result', f'{result.summary}\n\nReport: {result.report_path}', QtWidgets.QMessageBox.Ok, self)
            open_button = message.addButton('Open Report', QtWidgets.QMessageBox.ActionRole)
            message.exec()
            if message.clickedButton() is open_button:
                from universaldaq.testing import open_path_best_effort
                open_path_best_effort(result.report_path)
            self.statusBar().showMessage(result.summary, 8000)

        def _open_manual_test_checklist(self) -> None:
            active_root = self._testing_package_root() / 'ACTIVE'
            checklist = active_root / 'docs' / 'testing' / '20260515_02_manual-test-checklist.md'
            if not checklist.is_file():
                QtWidgets.QMessageBox.warning(self, 'Manual Test Checklist', f'Checklist not found: {checklist}')
                return
            from universaldaq.testing import open_path_best_effort
            opened = open_path_best_effort(checklist)
            self.statusBar().showMessage(f'Manual checklist: {checklist}' if opened else f'Open manually: {checklist}', 8000)

        def _open_latest_test_report_folder(self) -> None:
            folder = self._testing_package_root() / 'ACTIVE' / 'audit_reports' / 'testing'
            folder.mkdir(parents=True, exist_ok=True)
            from universaldaq.testing import open_path_best_effort
            opened = open_path_best_effort(folder)
            self.statusBar().showMessage(f'Testing report folder: {folder}' if opened else f'Open manually: {folder}', 8000)

        def _build_top_bar(self) -> QtWidgets.QFrame:
            frame = QtWidgets.QFrame()
            frame.setObjectName('persistentInfoBar')
            frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
            layout = QtWidgets.QHBoxLayout(frame)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(12)
            self._top_bar_labels: dict[str, Any] = {}
            self._top_bar_badges: dict[str, QtWidgets.QFrame] = {}
            badge_order = (
                ('mode', 'Mode'),
                ('session', 'Session'),
                ('device', 'Device/Scenario'),
                ('signal', 'Signal'),
                ('freshness', 'Freshness'),
                ('graph', 'Graph'),
                ('access', 'Access'),
                ('control', 'Control'),
                ('alarms', 'Alarms'),
            )
            for key, title in badge_order:
                badge = QtWidgets.QFrame()
                badge.setObjectName(f'topBadge_{key}')
                badge.setFrameShape(QtWidgets.QFrame.Box)
                badge_layout = QtWidgets.QHBoxLayout(badge)
                badge_layout.setContentsMargins(6, 2, 6, 2)
                badge_layout.setSpacing(6)
                title_label = QtWidgets.QLabel(f'{title}:')
                badge_layout.addWidget(title_label)
                if key == 'graph':
                    value = QtWidgets.QToolButton()
                    value.setPopupMode(QtWidgets.QToolButton.InstantPopup)
                    value.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
                    value.setAutoRaise(True)
                    menu = QtWidgets.QMenu(value)
                    for mode_id, label in (('primary', 'Primary'), ('compact_pip', 'PiP'), ('hidden', 'Hidden')):
                        action = menu.addAction(label)
                        action.triggered.connect(lambda checked=False, mode=mode_id: self._set_graph_mode_from_top_bar(mode))
                    value.setMenu(menu)
                    value.setToolTip('Choose graph presentation mode')
                else:
                    value = QtWidgets.QLabel('—')
                    value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                value.setObjectName(f'topBar_{key}')
                badge_layout.addWidget(value)
                layout.addWidget(badge)
                self._top_bar_labels[key] = value
                self._top_bar_badges[key] = badge
            layout.addStretch(1)
            return frame

        def _set_graph_mode_from_top_bar(self, mode: str) -> None:
            if mode == 'hidden':
                self._graph_presentation_override = 'hidden'
                self._apply_graph_presentation('hidden')
                return
            self._graph_presentation_override = mode
            self._apply_graph_presentation(mode)

        def _badge_palette(self, semantic: str) -> tuple[str, str, str]:
            palettes = {
                'good': ('#123524', '#1f7a4c', '#dff8e7'),
                'info': ('#15263d', '#2d6cdf', '#e7f1ff'),
                'warning': ('#3a2610', '#c98a16', '#fff4d8'),
                'critical': ('#431b1b', '#d94848', '#ffe3e3'),
                'muted': ('#232831', '#5c6773', '#d6dde6'),
                'neutral': ('#2b313a', '#7a8795', '#eef2f7'),
            }
            return palettes.get(semantic, palettes['neutral'])

        def _apply_badge_semantics(self, key: str, semantic: str) -> None:
            badge = self._top_bar_badges.get(key)
            if badge is None:
                return
            background, border, foreground = self._badge_palette(semantic)
            badge.setStyleSheet(
                f"QFrame#{badge.objectName()} {{ background: {background}; border: 1px solid {border}; border-radius: 6px; }}"
                f" QLabel {{ color: {foreground}; font-weight: 600; }}"
                f" QToolButton {{ color: {foreground}; font-weight: 700; background: transparent; border: none; padding: 0 2px; }}"
            )

        def _refresh_top_bar_semantics(self) -> None:
            mode_text = str(self._top_bar_labels.get('mode').text()).lower() if 'mode' in self._top_bar_labels else ''
            session_text = str(self._top_bar_labels.get('session').text()).lower() if 'session' in self._top_bar_labels else ''
            freshness_text = str(self._top_bar_labels.get('freshness').text()).lower() if 'freshness' in self._top_bar_labels else ''
            access_text = str(self._top_bar_labels.get('access').text()).lower() if 'access' in self._top_bar_labels else ''
            control_text = str(self._top_bar_labels.get('control').text()).lower() if 'control' in self._top_bar_labels else ''
            alarms_text = str(self._top_bar_labels.get('alarms').text()).lower() if 'alarms' in self._top_bar_labels else ''
            graph_text = str(self._graph_presentation).lower()
            self._apply_badge_semantics('mode', 'good' if mode_text == 'live' else 'info' if mode_text == 'user-demo' else 'muted')
            if 'disconnect' in session_text or 'failed' in session_text:
                self._apply_badge_semantics('session', 'critical')
            elif 'degraded' in session_text or 'pending' in session_text:
                self._apply_badge_semantics('session', 'warning')
            elif 'connected' in session_text:
                self._apply_badge_semantics('session', 'good')
            else:
                self._apply_badge_semantics('session', 'neutral')
            self._apply_badge_semantics('device', 'neutral')
            self._apply_badge_semantics('signal', 'neutral')
            if 'stale' in freshness_text or 'invalid' in freshness_text:
                self._apply_badge_semantics('freshness', 'critical')
            elif 'degraded' in freshness_text or 'aging' in freshness_text or 'pending' in freshness_text:
                self._apply_badge_semantics('freshness', 'warning')
            elif freshness_text in {'fresh', 'simulated'}:
                self._apply_badge_semantics('freshness', 'good' if freshness_text == 'fresh' else 'info')
            else:
                self._apply_badge_semantics('freshness', 'neutral')
            self._apply_badge_semantics('graph', 'muted' if graph_text == 'hidden' else 'info' if graph_text == 'compact_pip' else 'good')
            if 'unavailable' in access_text or 'missing' in access_text:
                self._apply_badge_semantics('access', 'critical')
            elif 'limited' in access_text or 'pending' in access_text or 'unknown' in access_text:
                self._apply_badge_semantics('access', 'warning')
            elif 'writable' in access_text or 'live' in access_text:
                self._apply_badge_semantics('access', 'good')
            elif 'readable' in access_text or 'simulated' in access_text:
                self._apply_badge_semantics('access', 'info')
            else:
                self._apply_badge_semantics('access', 'neutral')
            self._apply_badge_semantics('control', 'good' if control_text == 'armed_control' else 'warning' if control_text == 'view_only' else 'critical')
            if '0 active' in alarms_text or 'none' in alarms_text:
                self._apply_badge_semantics('alarms', 'muted')
            elif 'critical' in alarms_text or 'high' in alarms_text:
                self._apply_badge_semantics('alarms', 'critical')
            elif 'warning' in alarms_text or 'active' in alarms_text:
                self._apply_badge_semantics('alarms', 'warning')
            else:
                self._apply_badge_semantics('alarms', 'neutral')

        def _build_operate_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
            summary = QtWidgets.QFrame()
            summary_layout = QtWidgets.QHBoxLayout(summary)
            summary_layout.setContentsMargins(8, 6, 8, 6)
            self.active_signal_label = QtWidgets.QLabel('No active signal')
            self.active_signal_label.setStyleSheet('font-weight: 600; font-size: 15px;')
            self.active_value_label = QtWidgets.QLabel('—')
            self.active_value_label.setStyleSheet('font-weight: 700; font-size: 18px;')
            self.active_meta_label = QtWidgets.QLabel('Quality: simulated | Provenance: demo')
            summary_layout.addWidget(self.active_signal_label, 2)
            summary_layout.addWidget(self.active_value_label, 1)
            summary_layout.addWidget(self.active_meta_label, 3)
            layout.addWidget(summary)
            self.operate_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            splitter = self.operate_splitter
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.showGrid(x=True, y=True, alpha=0.18)
            self.plot_widget.setBackground('w')
            self.plot_widget.setLabel('bottom', 'Time', units='s')
            self.plot_widget.setLabel('left', 'Value')
            self.plot_widget.addLegend(offset=(10, 10))
            splitter.addWidget(self.plot_widget)
            self.legend_tree = QtWidgets.QTreeWidget()
            self.legend_tree.setHeaderLabels(['Trace', 'Value', 'Axis', 'State'])
            self.legend_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.legend_tree.itemSelectionChanged.connect(self._on_legend_selection_changed)
            self.legend_tree.itemChanged.connect(self._on_legend_item_changed)
            self.legend_tree.setMinimumWidth(180)
            splitter.addWidget(self.legend_tree)
            splitter.setSizes([1100, 260])
            layout.addWidget(splitter, 1)
            self.workspace_tabs.addTab(page, 'Operate')

        def _build_logic_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            self.logic_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            splitter = self.logic_splitter
            palette_panel = QtWidgets.QWidget()
            palette_layout = QtWidgets.QVBoxLayout(palette_panel)
            palette_layout.setContentsMargins(0, 0, 0, 0)
            self.logic_palette = QtWidgets.QListWidget()
            self.logic_palette.addItems(['Source', 'Filter', 'Math', 'Comparator', 'Sink'])
            self.logic_palette.itemDoubleClicked.connect(lambda item: self._add_logic_node(item.text()))
            add_logic_button = QtWidgets.QPushButton('Add Draft Node')
            add_logic_button.clicked.connect(lambda: self._add_logic_node(self.logic_palette.currentItem().text() if self.logic_palette.currentItem() else 'Source'))
            remove_logic_button = QtWidgets.QPushButton('Remove Last Node')
            remove_logic_button.clicked.connect(self._remove_last_logic_node)
            reset_logic_button = QtWidgets.QPushButton('Reset Draft Chain')
            reset_logic_button.clicked.connect(self._reset_logic_nodes)
            palette_layout.addWidget(self.logic_palette, 1)
            palette_layout.addWidget(add_logic_button)
            palette_layout.addWidget(remove_logic_button)
            palette_layout.addWidget(reset_logic_button)
            splitter.addWidget(palette_panel)
            self.logic_scene = QtWidgets.QGraphicsScene()
            self.logic_view = QtWidgets.QGraphicsView(self.logic_scene)
            splitter.addWidget(self.logic_view)
            self.logic_inspector = QtWidgets.QTreeWidget()
            self.logic_inspector.setHeaderLabels(['Property', 'Value'])
            splitter.addWidget(self.logic_inspector)
            splitter.setSizes([180, 760, 260])
            layout.addWidget(splitter, 1)
            self.logic_watch = QtWidgets.QPlainTextEdit()
            self.logic_watch.setReadOnly(True)
            self.logic_watch.setMaximumHeight(180)
            layout.addWidget(self.logic_watch)
            self.workspace_tabs.addTab(page, 'Logic Designer')

        def _build_session_review_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(page)
            self.session_review_list = QtWidgets.QListWidget()
            self.session_review_detail = QtWidgets.QPlainTextEdit()
            self.session_review_detail.setReadOnly(True)
            layout.addWidget(self.session_review_list, 1)
            layout.addWidget(self.session_review_detail, 2)
            self.workspace_tabs.addTab(page, 'Session Review')
            self.session_review_list.addItems(['Current demo session', 'Last exported graph setup'])
            self.session_review_list.currentTextChanged.connect(lambda text: self.session_review_detail.setPlainText(self._review_detail_text(text)))
            self.session_review_list.setCurrentRow(0)

        def _build_system_workspace(self) -> None:
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
            self.system_summary = QtWidgets.QPlainTextEdit()
            self.system_summary.setReadOnly(True)
            splitter.addWidget(self.system_summary)

            device_panel = QtWidgets.QWidget()
            device_layout = QtWidgets.QVBoxLayout(device_panel)
            device_layout.setContentsMargins(0, 0, 0, 0)
            self.device_io_scope_label = QtWidgets.QLabel('Device I/O Inspector — select a device to inspect its full I/O inventory and assign tags')
            self.device_io_scope_label.setStyleSheet('font-weight: 600;')
            device_layout.addWidget(self.device_io_scope_label)
            device_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            self.device_io_table = QtWidgets.QTableWidget(0, 8)
            self.device_io_table.setHorizontalHeaderLabels(['Endpoint', 'Internal Signal', 'Tag', 'Direction', 'Class', 'Access', 'Authority', 'Units'])
            self.device_io_table.horizontalHeader().setStretchLastSection(True)
            self.device_io_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.device_io_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.device_io_table.itemSelectionChanged.connect(self._on_device_io_selection_changed)
            device_splitter.addWidget(self.device_io_table)
            editor = QtWidgets.QWidget()
            editor_form = QtWidgets.QFormLayout(editor)
            self.device_io_context_label = QtWidgets.QLabel('No device selected')
            self.device_io_endpoint_label = QtWidgets.QLabel('—')
            self.device_io_internal_label = QtWidgets.QLabel('—')
            self.device_io_tag_edit = QtWidgets.QLineEdit()
            self.device_io_tag_edit.setPlaceholderText('Canonical tag / display name')
            self.device_io_tag_edit.editingFinished.connect(self._apply_device_tag_edit)
            self.device_io_authority_label = QtWidgets.QLabel('—')
            self.device_io_capability_label = QtWidgets.QLabel('—')
            self.device_io_note_label = QtWidgets.QLabel('Select an I/O row to inspect provenance, authority, and health')
            self.device_io_note_label.setWordWrap(True)
            apply_tag_button = QtWidgets.QPushButton('Apply Tag')
            apply_tag_button.clicked.connect(self._apply_device_tag_edit)
            editor_form.addRow('Context', self.device_io_context_label)
            editor_form.addRow('Endpoint', self.device_io_endpoint_label)
            editor_form.addRow('Internal Signal', self.device_io_internal_label)
            editor_form.addRow('Tag', self.device_io_tag_edit)
            editor_form.addRow('Authority', self.device_io_authority_label)
            editor_form.addRow('Access', self.device_io_capability_label)
            editor_form.addRow('Notes', self.device_io_note_label)
            editor_form.addRow(apply_tag_button)
            device_splitter.addWidget(editor)
            device_splitter.setSizes([860, 320])
            device_layout.addWidget(device_splitter, 1)
            splitter.addWidget(device_panel)

            self.authoritative_binding_summary = QtWidgets.QPlainTextEdit()
            self.authoritative_binding_summary.setReadOnly(True)
            self.authoritative_binding_summary.setMaximumHeight(150)
            splitter.addWidget(self.authoritative_binding_summary)

            mapping_panel = QtWidgets.QWidget()
            mapping_layout = QtWidgets.QVBoxLayout(mapping_panel)
            mapping_layout.setContentsMargins(0, 0, 0, 0)
            self.mapping_scope_label = QtWidgets.QLabel('Mapping Drafts / Preview — backend authority remains outside the shell')
            self.mapping_scope_label.setStyleSheet('font-weight: 600;')
            mapping_layout.addWidget(self.mapping_scope_label)
            mapping_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            self.mapping_table = QtWidgets.QTableWidget(0, 7)
            self.mapping_table.setHorizontalHeaderLabels(['Direction', 'Source Endpoint', 'Internal Signal', 'Destination Endpoint', 'Status', 'Units', 'Enabled'])
            self.mapping_table.horizontalHeader().setStretchLastSection(True)
            self.mapping_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.mapping_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.mapping_table.itemSelectionChanged.connect(self._on_mapping_selection_changed)
            mapping_splitter.addWidget(self.mapping_table)
            editor = QtWidgets.QWidget()
            editor_form = QtWidgets.QFormLayout(editor)
            self.mapping_direction_combo = QtWidgets.QComboBox(); self.mapping_direction_combo.addItems(['device_input_to_internal_signal', 'internal_signal_to_device_output'])
            self.mapping_source_combo = QtWidgets.QComboBox()
            self.mapping_internal_name_edit = QtWidgets.QLineEdit()
            self.mapping_destination_combo = QtWidgets.QComboBox()
            self.mapping_scale_spin = QtWidgets.QDoubleSpinBox(); self.mapping_scale_spin.setRange(-1_000_000, 1_000_000); self.mapping_scale_spin.setDecimals(4); self.mapping_scale_spin.setValue(1.0)
            self.mapping_offset_spin = QtWidgets.QDoubleSpinBox(); self.mapping_offset_spin.setRange(-1_000_000, 1_000_000); self.mapping_offset_spin.setDecimals(4)
            self.mapping_invert_checkbox = QtWidgets.QCheckBox('Invert signal')
            self.mapping_enabled_checkbox = QtWidgets.QCheckBox('Mapping enabled'); self.mapping_enabled_checkbox.setChecked(True)
            self.mapping_note_edit = QtWidgets.QPlainTextEdit(); self.mapping_note_edit.setPlaceholderText('Notes / provenance'); self.mapping_note_edit.setMaximumHeight(90)
            self.mapping_status_label = QtWidgets.QLabel('No draft selected — backend-applied mappings are not edited here yet')
            button_row = QtWidgets.QHBoxLayout()
            apply_button = QtWidgets.QPushButton('Save Draft Edit'); apply_button.clicked.connect(self._apply_mapping_edit)
            remove_button = QtWidgets.QPushButton('Mark Draft Unmapped'); remove_button.clicked.connect(self._remove_mapping)
            button_row.addWidget(apply_button)
            button_row.addWidget(remove_button)
            editor_form.addRow('Direction', self.mapping_direction_combo)
            editor_form.addRow('Source endpoint', self.mapping_source_combo)
            editor_form.addRow('Internal signal', self.mapping_internal_name_edit)
            editor_form.addRow('Destination endpoint', self.mapping_destination_combo)
            editor_form.addRow('Scale', self.mapping_scale_spin)
            editor_form.addRow('Offset', self.mapping_offset_spin)
            editor_form.addRow(self.mapping_invert_checkbox)
            editor_form.addRow(self.mapping_enabled_checkbox)
            editor_form.addRow('Status', self.mapping_status_label)
            editor_form.addRow('Notes', self.mapping_note_edit)
            editor_form.addRow(button_row)
            mapping_splitter.addWidget(editor)
            mapping_splitter.setSizes([860, 340])
            mapping_layout.addWidget(mapping_splitter, 1)
            splitter.addWidget(mapping_panel)
            splitter.setSizes([150, 360, 140, 340])
            layout.addWidget(splitter, 1)
            self.workspace_tabs.addTab(page, 'System')
            self._refresh_system_summary()

        def _build_right_control_dock(self) -> None:
            self.control_tabs = QtWidgets.QTabWidget()
            self.control_tab_indexes: dict[str, int] = {}
            self.control_tab_indexes['session'] = self.control_tabs.addTab(self._build_session_panel(), 'Session')
            self.control_tab_indexes['signals'] = self.control_tabs.addTab(self._build_signals_panel(), 'Signals')
            self.control_tab_indexes['trace'] = self.control_tabs.addTab(self._build_trace_inspector_panel(), 'Trace Inspector')
            self.control_tab_indexes['notes'] = self.control_tabs.addTab(self._build_notes_panel(), 'Notes')
            self.control_tab_indexes['diagnostics'] = self.control_tabs.addTab(self._build_diagnostics_panel(), 'Diagnostics')
            self.control_dock = self._wrap_panel('Control Column', self.control_tabs)
            self.control_dock.setMinimumWidth(240)

        def _build_bottom_log_dock(self) -> None:
            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(4, 4, 4, 4)
            toolbar = QtWidgets.QHBoxLayout()
            self.event_filter_combo = QtWidgets.QComboBox()
            self.event_filter_combo.addItems(['All', 'Diagnostics', 'Actions', 'Warnings', 'Alarms', 'Runtime'])
            self.event_filter_combo.currentTextChanged.connect(self._refresh_event_console)
            self.event_search_edit = QtWidgets.QLineEdit()
            self.event_search_edit.setPlaceholderText('Search events…')
            self.event_search_edit.textChanged.connect(self._refresh_event_console)
            toolbar.addWidget(QtWidgets.QLabel('Filter'))
            toolbar.addWidget(self.event_filter_combo)
            toolbar.addWidget(self.event_search_edit, 1)
            layout.addLayout(toolbar)
            self.event_table = QtWidgets.QTableWidget(0, 4)
            self.event_table.setHorizontalHeaderLabels(['Time', 'Severity', 'Category', 'Message'])
            self.event_table.horizontalHeader().setStretchLastSection(True)
            self.event_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.event_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.bottom_log = QtWidgets.QPlainTextEdit()
            self.bottom_log.setReadOnly(True)
            self.bottom_log.setMaximumHeight(90)
            self.bottom_log.hide()
            layout.addWidget(self.event_table, 1)
            layout.addWidget(self.bottom_log)
            self.bottom_dock = self._wrap_panel('Events / Diagnostics', container)
            self.bottom_dock.setMinimumHeight(150)

        def _build_explorer_dock(self) -> None:
            self.explorer_tabs = QtWidgets.QTabWidget()
            self.device_explorer = QtWidgets.QTreeWidget()
            self.device_explorer.setHeaderLabels(['Device / Endpoint', 'Capability', 'Runtime'])
            self.device_explorer.setMinimumWidth(180)
            self.device_explorer.itemSelectionChanged.connect(self._on_device_explorer_selection_changed)
            self.signal_explorer = QtWidgets.QTreeWidget()
            self.signal_explorer.setHeaderLabels(['Internal Signal', 'Source', 'Status'])
            self.logic_explorer = QtWidgets.QTreeWidget()
            self.logic_explorer.setHeaderLabels(['Logic / Mapping Surface'])
            self.explorer_tab_indexes: dict[str, int] = {}
            self.explorer_tab_indexes['device'] = self.explorer_tabs.addTab(self.device_explorer, 'Device Explorer')
            self.explorer_tab_indexes['signal'] = self.explorer_tabs.addTab(self.signal_explorer, 'Signal Explorer')
            self.explorer_tab_indexes['logic'] = self.explorer_tabs.addTab(self.logic_explorer, 'Logic Modules')
            self.explorer_dock = self._wrap_panel('Explorers', self.explorer_tabs)
            self.explorer_dock.setMinimumWidth(210)

        def _wrap_panel(self, title: str, child: QtWidgets.QWidget) -> QtWidgets.QFrame:
            panel = QtWidgets.QFrame()
            panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
            layout = QtWidgets.QVBoxLayout(panel)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(4)
            heading = QtWidgets.QLabel(title)
            heading.setStyleSheet('font-weight: 600; padding: 2px 4px;')
            layout.addWidget(heading)
            layout.addWidget(child, 1)
            return panel

        def _build_session_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QFormLayout(panel)
            self.demo_scenario_combo = QtWidgets.QComboBox()
            for scenario in self.demo_runtime.available_scenarios():
                self.demo_scenario_combo.addItem(scenario.display_name, scenario.scenario_id)
            idx = max(0, self.demo_scenario_combo.findData(self.demo_runtime.active_scenario_id))
            self.demo_scenario_combo.setCurrentIndex(idx)
            self.demo_scenario_combo.currentIndexChanged.connect(self._on_demo_scenario_changed)
            self.live_device_combo = QtWidgets.QComboBox()
            self.live_device_combo.currentIndexChanged.connect(self._refresh_capability_summary)
            self._refresh_live_device_inventory()
            self.connect_live_button = QtWidgets.QPushButton('Connect Live Device')
            self.connect_live_button.clicked.connect(self._connect_live_device)
            self.disconnect_live_button = QtWidgets.QPushButton('Disconnect')
            self.disconnect_live_button.clicked.connect(self._disconnect_live_device)
            self.arm_control_button = QtWidgets.QPushButton('Enter Armed Control')
            self.arm_control_button.clicked.connect(lambda: self._set_control_posture('armed_control'))
            self.view_only_button = QtWidgets.QPushButton('Return to View Only')
            self.view_only_button.clicked.connect(lambda: self._set_control_posture('view_only'))
            self.guarded_write_button = QtWidgets.QPushButton('Guarded Write DAC0 → 2.500 V')
            self.guarded_write_button.clicked.connect(self._perform_guarded_write)
            self.session_state_label = QtWidgets.QLabel('connected')
            self.runtime_state_label = QtWidgets.QLabel('USER-DEMO / simulated')
            self.control_posture_label = QtWidgets.QLabel(self.control_posture)
            self.capability_summary_label = QtWidgets.QLabel('Capability summary pending')
            self.capability_summary_label.setWordWrap(True)
            self.capability_reason_label = QtWidgets.QLabel('')
            self.capability_reason_label.setWordWrap(True)
            self.capability_reason_label.setStyleSheet('color: #c2410c;')
            layout.addRow('Demo Scenario', self.demo_scenario_combo)
            layout.addRow('Live Device', self.live_device_combo)
            layout.addRow(self.connect_live_button)
            layout.addRow(self.disconnect_live_button)
            layout.addRow('Session State', self.session_state_label)
            layout.addRow('Runtime', self.runtime_state_label)
            layout.addRow('Capability', self.capability_summary_label)
            layout.addRow('Access Note', self.capability_reason_label)
            layout.addRow('Control Posture', self.control_posture_label)
            layout.addRow(self.arm_control_button)
            layout.addRow(self.view_only_button)
            layout.addRow(self.guarded_write_button)
            return panel

        def _build_signals_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.signal_lens_combo = QtWidgets.QComboBox()
            for lens in self.spec.foundation.signal_lenses:
                self.signal_lens_combo.addItem(lens.display_name, lens.lens_id)
            index = max(0, self.signal_lens_combo.findData(self.selected_lens_id))
            self.signal_lens_combo.setCurrentIndex(index)
            self.signal_lens_combo.currentIndexChanged.connect(self._on_lens_changed)
            self.available_signals_list = QtWidgets.QListWidget()
            self.available_signals_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            add_btn = QtWidgets.QPushButton('Add Selected Trace(s)')
            add_btn.clicked.connect(self._add_selected_signals)
            remove_btn = QtWidgets.QPushButton('Remove Selected Trace')
            remove_btn.clicked.connect(self._remove_selected_trace)
            layout.addWidget(self.signal_lens_combo)
            layout.addWidget(self.available_signals_list, 1)
            layout.addWidget(add_btn)
            layout.addWidget(remove_btn)
            return panel

        def _build_trace_inspector_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.trace_hint_label = QtWidgets.QLabel('Select a legend row to edit its style, axis, markers, and emphasis.')
            self.trace_hint_label.setWordWrap(True)
            layout.addWidget(self.trace_hint_label)
            form = QtWidgets.QFormLayout()
            self.trace_name_label = QtWidgets.QLabel('No trace selected')
            self.trace_color_button = QtWidgets.QPushButton('Choose…')
            self.trace_color_button.clicked.connect(self._choose_trace_color)
            self.trace_width_spin = QtWidgets.QSpinBox(); self.trace_width_spin.setRange(1, 8)
            self.trace_width_spin.valueChanged.connect(self._apply_trace_style_from_controls)
            self.trace_line_combo = QtWidgets.QComboBox(); self.trace_line_combo.addItems(['solid', 'dashed', 'dotted'])
            self.trace_line_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            self.trace_marker_combo = QtWidgets.QComboBox(); self.trace_marker_combo.addItems(['none', 'circle', 'square'])
            self.trace_marker_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            self.trace_marker_size_spin = QtWidgets.QSpinBox(); self.trace_marker_size_spin.setRange(0, 12)
            self.trace_marker_size_spin.valueChanged.connect(self._apply_trace_style_from_controls)
            self.trace_axis_combo = QtWidgets.QComboBox(); self.trace_axis_combo.addItems(['primary', 'secondary'])
            self.trace_axis_combo.setToolTip('Primary axis is active now. Secondary-axis selection is stored as preview-only in this package.')
            self.trace_axis_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            self.trace_glow_checkbox = QtWidgets.QCheckBox('Glow edge')
            self.trace_glow_checkbox.setEnabled(False)
            self.trace_glow_checkbox.setToolTip('Preview-only in this package; line and marker styling are active.')
            self.trace_glow_checkbox.toggled.connect(self._apply_trace_style_from_controls)
            self.trace_blink_combo = QtWidgets.QComboBox(); self.trace_blink_combo.addItems(['off', 'selected', 'critical_only'])
            self.trace_blink_combo.setEnabled(False)
            self.trace_blink_combo.setToolTip('Preview-only in this package; line and marker styling are active.')
            self.trace_blink_combo.currentTextChanged.connect(self._apply_trace_style_from_controls)
            reset_button = QtWidgets.QPushButton('Reset Trace Style')
            reset_button.clicked.connect(self._reset_active_trace_style)
            form.addRow('Trace', self.trace_name_label)
            form.addRow('Color', self.trace_color_button)
            form.addRow('Line width', self.trace_width_spin)
            form.addRow('Line style', self.trace_line_combo)
            form.addRow('Marker', self.trace_marker_combo)
            form.addRow('Marker size', self.trace_marker_size_spin)
            form.addRow('Axis', self.trace_axis_combo)
            form.addRow(self.trace_glow_checkbox)
            form.addRow('Blink', self.trace_blink_combo)
            form.addRow(reset_button)
            layout.addLayout(form)
            layout.addStretch(1)
            return panel

        def _build_notes_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.note_entry = QtWidgets.QPlainTextEdit()
            self.note_entry.setPlaceholderText('Add a timestamped operator note…')
            self.note_list = QtWidgets.QListWidget()
            add_btn = QtWidgets.QPushButton('Add Note')
            add_btn.clicked.connect(self._add_note)
            layout.addWidget(self.note_entry)
            layout.addWidget(add_btn)
            layout.addWidget(self.note_list, 1)
            return panel

        def _build_diagnostics_panel(self) -> QtWidgets.QWidget:
            panel = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(panel)
            self.diagnostics_text = QtWidgets.QPlainTextEdit()
            self.diagnostics_text.setReadOnly(True)
            export_btn = QtWidgets.QPushButton('Export Diagnostics…')
            export_btn.clicked.connect(self._export_diagnostics)
            layout.addWidget(self.diagnostics_text, 1)
            layout.addWidget(export_btn)
            return panel

        def _refresh_signal_inventory(self) -> None:
            self.available_signals_list.clear()
            self.device_explorer.clear()
            self.signal_explorer.clear()
            self.logic_explorer.clear()
            descriptors = tuple(self.runtime.signal_descriptors(lens_id=self.selected_lens_id))
            lens_id = self.signal_lens_combo.currentData() if hasattr(self, 'signal_lens_combo') else self.selected_lens_id
            device_context_key, device_context_label = self._current_device_context()
            self._selected_device_context_key = device_context_key
            self._selected_device_context_label = device_context_label

            device_capability = 'simulated' if self.runtime_mode != 'LIVE' else 'live device pending'
            runtime_label = self.runtime_mode
            live_record = self._selected_capability_record() if self.runtime_mode == 'LIVE' else None
            if live_record is not None:
                device_capability = f"{live_record.capability_mode} / {live_record.read_state} / {live_record.write_state}"
                runtime_label = live_record.limited_access_reason or live_record.hardware_mode
            device_item = QtWidgets.QTreeWidgetItem([device_context_label, device_capability, runtime_label])
            device_item.setData(0, QtCore.Qt.UserRole, {'device_context_key': device_context_key, 'row_id': None})
            self.device_explorer.addTopLevelItem(device_item)

            for descriptor in descriptors:
                signal_id = descriptor.signal_id
                label = self._label_for_signal(signal_id)
                item = QtWidgets.QListWidgetItem(label)
                item.setData(QtCore.Qt.UserRole, descriptor.signal_id)
                self.available_signals_list.addItem(item)
                hardware_name = descriptor.label_for_lens('hardware')
                logical_name = descriptor.label_for_lens('logical')
                capability = 'writable' if getattr(descriptor, 'write_safe', False) else 'readable'
                child_runtime = runtime_label
                if self.runtime_mode == 'LIVE' and live_record is not None:
                    capability = f"{capability} / {live_record.capability_mode}"
                    child_runtime = live_record.limited_access_reason or f"{live_record.read_state} / {live_record.write_state}"
                child = QtWidgets.QTreeWidgetItem([hardware_name, capability, child_runtime])
                child.setData(0, QtCore.Qt.UserRole, {'device_context_key': device_context_key, 'row_id': signal_id})
                device_item.addChild(child)
                signal_item = QtWidgets.QTreeWidgetItem([label, hardware_name, getattr(descriptor, 'source_class', 'signal')])
                signal_item.setData(0, QtCore.Qt.UserRole, signal_id)
                self.signal_explorer.addTopLevelItem(signal_item)
                logic_item = QtWidgets.QTreeWidgetItem([label])
                logic_item.setData(0, QtCore.Qt.UserRole, signal_id)
                self.logic_explorer.addTopLevelItem(logic_item)
            for widget in (self.device_explorer, self.signal_explorer, self.logic_explorer):
                widget.expandAll()
            self.device_explorer.setCurrentItem(device_item)
            if hasattr(self, 'mapping_table'):
                rows = build_mapping_rows(
                    signal_descriptors=descriptors,
                    writable_targets=getattr(self.runtime, 'writable_targets', lambda: ())(),
                    runtime_mode=self.runtime_mode,
                )
                self._mapping_rows = {row.row_id: {
                    'row_id': row.row_id,
                    'direction': row.direction.value,
                    'source_endpoint': row.source_endpoint,
                    'internal_signal_name': row.internal_signal_name,
                    'destination_endpoint': row.destination_endpoint,
                    'status': row.status.value,
                    'capability_label': row.capability_label,
                    'units': row.units,
                    'scale': row.scale,
                    'offset': row.offset,
                    'invert': row.invert,
                    'enabled': row.enabled,
                    'live_capable': row.live_capable,
                    'simulated': row.simulated,
                    'note': row.note,
                    'provenance_label': row.provenance_label,
                } for row in rows}
                self._populate_mapping_table()
                self._populate_mapping_editor_choices()
            self._refresh_device_io_inventory()

        def _refresh_device_io_inventory(self) -> None:
            if not hasattr(self, 'device_io_table'):
                return
            device_context_key = self._selected_device_context_key or self._current_device_context()[0]
            descriptors = tuple(self.runtime.signal_descriptors(lens_id=self.selected_lens_id))
            mapping_rows = build_mapping_rows(
                signal_descriptors=descriptors,
                writable_targets=getattr(self.runtime, 'writable_targets', lambda: ())(),
                runtime_mode=self.runtime_mode,
            )
            self._device_io_rows = [
                {
                    'row_id': row.row_id,
                    'signal_id': row.signal_id,
                    'endpoint_label': row.endpoint_label,
                    'internal_signal_name': row.internal_signal_name,
                    'tag_name': row.tag_name,
                    'direction': row.direction,
                    'source_class': row.source_class,
                    'capability_label': row.capability_label,
                    'authority_state': row.authority_state,
                    'units': row.units,
                    'health_label': row.health_label,
                    'provenance_label': row.provenance_label,
                    'note': row.note,
                }
                for row in build_device_io_rows(
                    device_context_key=device_context_key,
                    signal_descriptors=descriptors,
                    mapping_rows=mapping_rows,
                    authoritative_rows=self._authoritative_binding_rows,
                    tag_names_by_signal=self._tag_names_by_signal,
                    runtime_mode=self.runtime_mode,
                    health_label=self.runtime.connection_state if self.runtime_mode == 'LIVE' else 'simulated',
                )
            ]
            self.device_io_scope_label.setText(f'Device I/O Inspector — {self._selected_device_context_label}')
            self._populate_device_io_table()

        def _populate_device_io_table(self) -> None:
            if not hasattr(self, 'device_io_table'):
                return
            rows = list(self._device_io_rows)
            self.device_io_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row['endpoint_label'],
                    row['internal_signal_name'],
                    row['tag_name'],
                    row['direction'],
                    row['source_class'],
                    row['capability_label'],
                    row['authority_state'],
                    row['units'],
                ]
                for col_index, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setData(QtCore.Qt.UserRole, row['row_id'])
                    self.device_io_table.setItem(row_index, col_index, item)
            self.device_io_table.resizeColumnsToContents()
            if rows:
                self.device_io_table.selectRow(0)
                self._on_device_io_selection_changed()

        def _selected_device_io_row_id(self) -> str | None:
            if not hasattr(self, 'device_io_table'):
                return None
            items = self.device_io_table.selectedItems()
            if not items:
                return None
            return items[0].data(QtCore.Qt.UserRole)

        def _on_device_io_selection_changed(self) -> None:
            row_id = self._selected_device_io_row_id()
            if row_id is None:
                return
            row = next((row for row in self._device_io_rows if row['row_id'] == row_id), None)
            if row is None:
                return
            self.device_io_context_label.setText(self._selected_device_context_label)
            self.device_io_endpoint_label.setText(row['endpoint_label'])
            self.device_io_internal_label.setText(row['internal_signal_name'])
            self.device_io_tag_edit.blockSignals(True)
            self.device_io_tag_edit.setText(row['tag_name'])
            self.device_io_tag_edit.blockSignals(False)
            self.device_io_authority_label.setText(row['authority_state'])
            self.device_io_capability_label.setText(row['capability_label'])
            note_parts = [row['health_label'], row['provenance_label'], row['note']]
            self.device_io_note_label.setText(' | '.join(part for part in note_parts if part))
            if row.get('signal_id'):
                self._set_selected_trace(row['signal_id'])

        def _apply_device_tag_edit(self) -> None:
            row_id = self._selected_device_io_row_id()
            if row_id is None:
                return
            row = next((row for row in self._device_io_rows if row['row_id'] == row_id), None)
            if row is None:
                return
            new_tag = self.device_io_tag_edit.text().strip()
            signal_id = row['signal_id']
            if not signal_id:
                return
            if new_tag:
                self._tag_names_by_signal[signal_id] = new_tag
            else:
                self._tag_names_by_signal.pop(signal_id, None)
            self._trace_name_by_signal.pop(signal_id, None)
            self._save_tag_names()
            self._refresh_signal_inventory()
            self._sync_trace_inspector()
            self.statusBar().showMessage(f'Updated canonical tag: {self._label_for_signal(signal_id)}', 2500)

        def _on_device_explorer_selection_changed(self) -> None:
            item = self.device_explorer.currentItem() if hasattr(self, 'device_explorer') else None
            if item is None:
                return
            payload = item.data(0, QtCore.Qt.UserRole) or {}
            device_context_key = payload.get('device_context_key')
            if device_context_key:
                self._selected_device_context_key = str(device_context_key)
                self._selected_device_context_label = item.text(0) if item.parent() is None else item.parent().text(0)
            row_id = payload.get('row_id')
            self._refresh_device_io_inventory()
            if row_id:
                for row_index, row in enumerate(self._device_io_rows):
                    if row['row_id'] == row_id:
                        self.device_io_table.selectRow(row_index)
                        break

        def _populate_mapping_table(self) -> None:
            if not hasattr(self, 'mapping_table'):
                return
            rows = list(self._mapping_rows.values())
            self.mapping_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row['direction'],
                    row['source_endpoint'],
                    row['internal_signal_name'],
                    row['destination_endpoint'],
                    row['status'],
                    row['units'],
                    'yes' if row['enabled'] else 'no',
                ]
                for col_index, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setData(QtCore.Qt.UserRole, row['row_id'])
                    self.mapping_table.setItem(row_index, col_index, item)
            self.mapping_table.resizeColumnsToContents()

        def _populate_mapping_editor_choices(self) -> None:
            if not hasattr(self, 'mapping_source_combo'):
                return
            self.mapping_source_combo.blockSignals(True)
            self.mapping_destination_combo.blockSignals(True)
            self.mapping_source_combo.clear()
            self.mapping_destination_combo.clear()
            self.mapping_source_combo.addItem('', '')
            self.mapping_destination_combo.addItem('', '')
            descriptors = tuple(self.runtime.signal_descriptors(lens_id=self.selected_lens_id))
            for descriptor in descriptors:
                self.mapping_source_combo.addItem(descriptor.label_for_lens('hardware'), descriptor.label_for_lens('hardware'))
                self.mapping_destination_combo.addItem(descriptor.label_for_lens('hardware'), descriptor.label_for_lens('hardware'))
            for target in getattr(self.runtime, 'writable_targets', lambda: ())():
                label = getattr(target, 'display_name', getattr(target, 'point_id', ''))
                self.mapping_destination_combo.addItem(str(label), str(label))
            self.mapping_source_combo.blockSignals(False)
            self.mapping_destination_combo.blockSignals(False)

        def _selected_mapping_row_id(self) -> str | None:
            if not hasattr(self, 'mapping_table'):
                return None
            items = self.mapping_table.selectedItems()
            if not items:
                return None
            return items[0].data(QtCore.Qt.UserRole)

        def _on_mapping_selection_changed(self) -> None:
            row_id = self._selected_mapping_row_id()
            if row_id is None:
                self.mapping_status_label.setText('No draft selected — backend-applied mappings are not edited here yet')
                return
            row = self._mapping_rows.get(row_id)
            if row is None:
                self.mapping_status_label.setText('Selected mapping missing')
                return
            self.mapping_direction_combo.setCurrentText(str(row['direction']))
            self.mapping_source_combo.setCurrentText(str(row['source_endpoint']))
            self.mapping_internal_name_edit.setText(str(row['internal_signal_name']))
            self.mapping_destination_combo.setCurrentText(str(row['destination_endpoint']))
            self.mapping_scale_spin.setValue(float(row['scale']))
            self.mapping_offset_spin.setValue(float(row['offset']))
            self.mapping_invert_checkbox.setChecked(bool(row['invert']))
            self.mapping_enabled_checkbox.setChecked(bool(row['enabled']))
            self.mapping_note_edit.setPlainText(str(row['note']))
            self.mapping_status_label.setText(f"{row['status']} — {row['capability_label']}")

        def _apply_mapping_edit(self) -> None:
            row_id = self._selected_mapping_row_id() or f"custom::{self.mapping_internal_name_edit.text().strip() or self.mapping_destination_combo.currentText().strip() or self.mapping_source_combo.currentText().strip()}"
            if row_id == 'custom::':
                self.statusBar().showMessage('Mapping edit requires at least one endpoint or signal name', 2500)
                return
            source = self.mapping_source_combo.currentText().strip()
            internal_name = self.mapping_internal_name_edit.text().strip()
            destination = self.mapping_destination_combo.currentText().strip()
            direction = self.mapping_direction_combo.currentText()
            if direction == 'device_input_to_internal_signal' and not source:
                status = 'missing_source'
            elif direction == 'internal_signal_to_device_output' and not destination:
                status = 'missing_destination'
            elif not internal_name:
                status = 'invalid'
            else:
                status = 'mapped'
            self._mapping_rows[row_id] = {
                'row_id': row_id,
                'direction': direction,
                'source_endpoint': source,
                'internal_signal_name': internal_name,
                'destination_endpoint': destination,
                'status': status,
                'capability_label': 'shell_draft_non_authoritative',
                'units': '',
                'scale': float(self.mapping_scale_spin.value()),
                'offset': float(self.mapping_offset_spin.value()),
                'invert': bool(self.mapping_invert_checkbox.isChecked()),
                'enabled': bool(self.mapping_enabled_checkbox.isChecked()),
                'live_capable': self.runtime_mode == 'LIVE',
                'simulated': self.runtime_mode != 'LIVE',
                'note': self.mapping_note_edit.toPlainText().strip(),
                'provenance_label': f'{source} ↔ {internal_name or destination}',
            }
            self._populate_mapping_table()
            self._refresh_system_summary()
            self.statusBar().showMessage(f'Saved shell draft only: {row_id}', 2500)

        def _remove_mapping(self) -> None:
            row_id = self._selected_mapping_row_id()
            if row_id is None:
                return
            row = self._mapping_rows.get(row_id)
            if row is None:
                return
            row['status'] = 'unmapped'
            row['enabled'] = False
            self._populate_mapping_table()
            self._refresh_system_summary()
            self.statusBar().showMessage(f'Marked shell draft unmapped: {row_id}', 2500)

        def _refresh_event_console(self) -> None:
            if not hasattr(self, 'event_table'):
                return
            category_filter = self.event_filter_combo.currentText() if hasattr(self, 'event_filter_combo') else 'All'
            search_text = self.event_search_edit.text().strip().lower() if hasattr(self, 'event_search_edit') else ''
            visible_rows = []
            for row in self._event_rows:
                if category_filter == 'Warnings' and row['severity'] != 'warning':
                    continue
                if category_filter == 'Alarms' and row['category'] != 'Alarms':
                    continue
                if category_filter not in {'All', 'Warnings', 'Alarms'} and row['category'] != category_filter:
                    continue
                haystack = ' '.join(row.values()).lower()
                if search_text and search_text not in haystack:
                    continue
                visible_rows.append(row)
            visible_rows = visible_rows[-200:]
            self.event_table.setRowCount(len(visible_rows))
            for row_index, row in enumerate(visible_rows):
                for col_index, key in enumerate(('timestamp_label', 'severity', 'category', 'message')):
                    self.event_table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(row[key]))
            self.event_table.resizeColumnsToContents()

        def _ensure_default_trace_selection(self) -> None:
            restored_active = self.settings.value('ui/active_traces', '', type=str)
            restored_signal_ids = [item for item in restored_active.split('|') if item]
            if restored_signal_ids:
                for signal_id in restored_signal_ids:
                    self._ensure_trace(signal_id)
            else:
                for descriptor in self.runtime.signal_descriptors()[: min(3, len(self.runtime.signal_descriptors()))]:
                    self._ensure_trace(descriptor.signal_id)
            selected_signal_id = self.settings.value('ui/selected_trace', '', type=str)
            if selected_signal_id and selected_signal_id in self._trace_states:
                self._set_selected_trace(selected_signal_id)
            elif self._trace_states:
                self._set_selected_trace(next(iter(self._trace_states.keys())))

        def _ensure_trace(self, signal_id: str) -> None:
            if signal_id in self._trace_states:
                return
            style = self._initial_style_for_signal(signal_id)
            state = _TraceState(signal_id=signal_id, style=style)
            state.main_item = self.plot_widget.plot([], [], name=self._label_for_signal(signal_id), **self._trace_render_kwargs(style))
            state.overlay_item = self.plot_widget.plot([], [], pen=None)
            state.overlay_item.setZValue(-1)
            self._trace_states[signal_id] = state
            row = QtWidgets.QTreeWidgetItem([self._label_for_signal(signal_id), '—', style.get('axis_assignment', 'primary'), 'normal'])
            row.setFlags(row.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            row.setCheckState(0, QtCore.Qt.Checked)
            row.setData(0, QtCore.Qt.UserRole, signal_id)
            self.legend_tree.addTopLevelItem(row)
            self._legend_rows[signal_id] = row

        def _trace_render_kwargs(self, style: dict[str, Any]) -> dict[str, Any]:
            kwargs: dict[str, Any] = {'pen': _pen_from_style(pg, QtCore, style)}
            marker = {
                'none': None,
                'circle': 'o',
                'square': 's',
            }.get(str(style.get('marker_style', 'none')), None)
            if marker is not None and int(style.get('marker_size', 0) or 0) > 0:
                kwargs.update(
                    {
                        'symbol': marker,
                        'symbolSize': int(style.get('marker_size', 0) or 0),
                        'symbolBrush': style.get('color', '#5dade2'),
                        'symbolPen': style.get('color', '#5dade2'),
                    }
                )
            else:
                kwargs['symbol'] = None
            return kwargs

        def _rerender_trace(self, signal_id: str) -> None:
            state = self._trace_states.get(signal_id)
            if state is None or state.main_item is None or state.overlay_item is None:
                return
            series = self.runtime.trace_series(signal_id)
            if state.visible:
                state.main_item.setData(series.x_values, series.y_values, **self._trace_render_kwargs(state.style))
                state.overlay_item.setData(series.x_values, series.y_values, pen=self._overlay_pen_for_state(state=state, severity='normal'))
            else:
                state.main_item.setData([], [])
                state.overlay_item.setData([], [])

        def _initial_style_for_signal(self, signal_id: str) -> dict[str, Any]:
            saved_styles = self._load_trace_styles()
            if signal_id in saved_styles:
                return dict(saved_styles[signal_id])
            catalog = self.spec.foundation.trace_style_catalog
            if signal_id.endswith('dac_cmd'):
                base = catalog.get('selected')
            else:
                base = catalog.get('base')
            style = asdict(base) if base is not None else {
                'color': '#5dade2',
                'line_width': 2,
                'line_pattern': 'solid',
                'marker_style': 'none',
                'marker_size': 0,
                'opacity_percent': 100,
                'glow_edge': False,
                'selected_highlight': False,
                'blink_mode': 'off',
                'axis_assignment': 'primary',
                'alarm_overlay_policy': 'severity_outline',
                'persistable': True,
            }
            style['selected_highlight'] = False
            return style

        def _load_trace_styles(self) -> dict[str, dict[str, Any]]:
            raw = self.settings.value('ui/trace_styles', '', type=str)
            if not raw:
                return {}
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return {str(key): dict(value) for key, value in payload.items() if isinstance(value, dict)}

        def _save_trace_styles(self) -> None:
            payload = {signal_id: state.style for signal_id, state in self._trace_states.items()}
            self.settings.setValue('ui/trace_styles', json.dumps(payload, sort_keys=True))

        def _render_step(self) -> None:
            snapshot = self.runtime.step()
            selected_snapshot = None
            active_alarm_count = 0
            highest = 'none'
            severity_rank = {'warning': 1, 'high': 2, 'critical': 3}
            for signal_snapshot in snapshot.signal_snapshots:
                severity = signal_snapshot.alarm_severity
                if severity != 'normal':
                    active_alarm_count += 1
                    if severity_rank.get(severity, 0) > severity_rank.get(highest, 0):
                        highest = severity
                state = self._trace_states.get(signal_snapshot.descriptor.signal_id)
                if state is None:
                    continue
                series = self.runtime.trace_series(signal_snapshot.descriptor.signal_id)
                if state.visible:
                    state.main_item.setData(series.x_values, series.y_values, **self._trace_render_kwargs(state.style))
                    overlay_pen = self._overlay_pen_for_state(state=state, severity=severity)
                    state.overlay_item.setData(series.x_values, series.y_values, pen=overlay_pen)
                else:
                    state.main_item.setData([], [])
                    state.overlay_item.setData([], [])
                row = self._legend_rows.get(signal_snapshot.descriptor.signal_id)
                if row is not None:
                    row.setText(0, self._label_for_signal(signal_snapshot.descriptor.signal_id))
                    row.setText(1, f'{signal_snapshot.value:0.3f} {signal_snapshot.descriptor.units or ""}'.strip())
                    row.setText(2, '2nd' if state.style.get('axis_assignment') == 'secondary' else '1st')
                    row.setText(3, severity)
                if signal_snapshot.descriptor.signal_id == self._active_signal_id:
                    selected_snapshot = signal_snapshot
            if self.runtime_mode == 'LIVE':
                self._top_bar_labels['mode'].setText('LIVE')
                self._top_bar_labels['session'].setText(snapshot.connection_state)
                self._top_bar_labels['device'].setText(snapshot.device_label)
                self._top_bar_labels['control'].setText(self.control_posture)
                capability = self._selected_capability_record()
                access_label = 'live device pending' if capability is None else f"{capability.capability_mode} / {capability.read_state} / {capability.write_state}"
                self._top_bar_labels['access'].setText(access_label)
                self._top_bar_labels['alarms'].setText(f'{active_alarm_count} active / highest {highest}')
                self._top_bar_labels['signal'].setText('—' if selected_snapshot is None else self._label_for_signal(selected_snapshot.descriptor.signal_id))
                self._top_bar_labels['freshness'].setText('pending' if selected_snapshot is None else selected_snapshot.freshness_label)
                self.session_state_label.setText(snapshot.connection_state)
                self.runtime_state_label.setText(f'LIVE / {snapshot.runtime_source_label}')
                self.control_posture_label.setText(self.control_posture)
                self.demo_scenario_combo.setEnabled(False)
                self.connect_live_button.setEnabled(True)
                self.disconnect_live_button.setEnabled(snapshot.connection_state == 'connected')
                self.guarded_write_button.setEnabled(True)
                self.arm_control_button.setEnabled(snapshot.connection_state == 'connected')
            else:
                self._top_bar_labels['mode'].setText('USER-DEMO')
                self._top_bar_labels['session'].setText('connected')
                self._top_bar_labels['device'].setText(snapshot.scenario.display_name)
                self._top_bar_labels['control'].setText(self.control_posture)
                self._top_bar_labels['access'].setText('user-demo / simulated')
                self._top_bar_labels['alarms'].setText(f'{active_alarm_count} active / highest {highest}')
                self._top_bar_labels['signal'].setText('—' if selected_snapshot is None else self._label_for_signal(selected_snapshot.descriptor.signal_id))
                self._top_bar_labels['freshness'].setText('simulated' if selected_snapshot is None else selected_snapshot.freshness_label)
                self.session_state_label.setText('connected')
                self.runtime_state_label.setText(f'USER-DEMO / {snapshot.scenario.display_name}')
                self.control_posture_label.setText(self.control_posture)
                self.demo_scenario_combo.setEnabled(True)
                self.connect_live_button.setEnabled(True)
                self.disconnect_live_button.setEnabled(False)
                self.guarded_write_button.setEnabled(True)
                self.arm_control_button.setEnabled(True)
            self.bottom_log.setPlainText('\n'.join(snapshot.event_log))
            self._event_rows = [
                {
                    'timestamp_label': row.timestamp_label,
                    'severity': row.severity,
                    'category': row.category,
                    'message': row.message,
                }
                for row in derive_event_console_rows(snapshot.event_log, elapsed_seconds=snapshot.elapsed_seconds)
            ]
            self._refresh_event_console()
            if selected_snapshot is not None:
                self.active_signal_label.setText(self._label_for_signal(selected_snapshot.descriptor.signal_id))
                self.active_value_label.setText(f'{selected_snapshot.value:0.3f} {selected_snapshot.descriptor.units or ""}'.strip())
                provenance = getattr(selected_snapshot, 'runtime_source_label', 'demo')
                self.active_meta_label.setText(
                    f'Quality: {selected_snapshot.quality_label} | Freshness: {selected_snapshot.freshness_label} | Alarm: {selected_snapshot.alarm_severity} | Runtime: {provenance}'
                )
            else:
                self.active_signal_label.setText('No active signal')
                self.active_value_label.setText('—')
                self.active_meta_label.setText('No active signal bound')
            self._refresh_top_bar_semantics()
            self._render_pip_overlay(snapshot)
            self._refresh_diagnostics(snapshot)
            self._refresh_session_review(snapshot)
            self._refresh_logic_watch(snapshot)
            self._refresh_system_summary()


        def _overlay_pen_for_state(self, *, state: _TraceState, severity: str) -> Any:
            if severity == 'critical':
                return _pen_from_style(pg, QtCore, state.style, color_override='#c0392b', width_offset=4)
            if severity == 'high':
                return _pen_from_style(pg, QtCore, state.style, color_override='#e67e22', width_offset=3)
            if severity == 'warning':
                return _pen_from_style(pg, QtCore, state.style, color_override='#f1c40f', width_offset=2)
            if state.selected:
                return _pen_from_style(pg, QtCore, state.style, color_override='#2c3e50', width_offset=2)
            return None

        def _label_for_signal(self, signal_id: str) -> str:
            if signal_id in self._tag_names_by_signal and self._tag_names_by_signal[signal_id].strip():
                label = self._tag_names_by_signal[signal_id].strip()
                self._trace_name_by_signal[signal_id] = label
                return label
            lens_id = self.signal_lens_combo.currentData() if hasattr(self, 'signal_lens_combo') else self.selected_lens_id
            for descriptor in self.runtime.signal_descriptors(lens_id=lens_id):
                if descriptor.signal_id == signal_id:
                    label = descriptor.label_for_lens(lens_id)
                    self._trace_name_by_signal[signal_id] = label
                    return label
            return self._trace_name_by_signal.get(signal_id, signal_id)

        def _set_selected_trace(self, signal_id: str) -> None:
            self._active_signal_id = signal_id
            for candidate_id, state in self._trace_states.items():
                state.selected = candidate_id == signal_id
                state.style['selected_highlight'] = state.selected
            row = self._legend_rows.get(signal_id)
            if row is not None:
                self.legend_tree.setCurrentItem(row)
            self._sync_trace_inspector()
            self.settings.setValue('ui/selected_trace', signal_id)

        def _sync_trace_inspector(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None or signal_id not in self._trace_states:
                self.trace_name_label.setText('No trace selected')
                return
            state = self._trace_states[signal_id]
            self.trace_name_label.setText(self._label_for_signal(signal_id))
            self.trace_color_button.setText(state.style.get('color', '#5dade2'))
            self.trace_width_spin.blockSignals(True); self.trace_width_spin.setValue(int(state.style.get('line_width', 2))); self.trace_width_spin.blockSignals(False)
            self.trace_line_combo.blockSignals(True); self.trace_line_combo.setCurrentText(state.style.get('line_pattern', 'solid')); self.trace_line_combo.blockSignals(False)
            self.trace_marker_combo.blockSignals(True); self.trace_marker_combo.setCurrentText(state.style.get('marker_style', 'none')); self.trace_marker_combo.blockSignals(False)
            self.trace_marker_size_spin.blockSignals(True); self.trace_marker_size_spin.setValue(int(state.style.get('marker_size', 0))); self.trace_marker_size_spin.blockSignals(False)
            self.trace_axis_combo.blockSignals(True); self.trace_axis_combo.setCurrentText(state.style.get('axis_assignment', 'primary')); self.trace_axis_combo.blockSignals(False)
            self.trace_glow_checkbox.blockSignals(True); self.trace_glow_checkbox.setChecked(bool(state.style.get('glow_edge', False))); self.trace_glow_checkbox.blockSignals(False)
            self.trace_blink_combo.blockSignals(True); self.trace_blink_combo.setCurrentText(state.style.get('blink_mode', 'off')); self.trace_blink_combo.blockSignals(False)

        def _apply_trace_style_from_controls(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None or signal_id not in self._trace_states:
                return
            state = self._trace_states[signal_id]
            state.style.update(
                {
                    'color': self.trace_color_button.text(),
                    'line_width': int(self.trace_width_spin.value()),
                    'line_pattern': self.trace_line_combo.currentText(),
                    'marker_style': self.trace_marker_combo.currentText(),
                    'marker_size': int(self.trace_marker_size_spin.value()),
                    'axis_assignment': self.trace_axis_combo.currentText(),
                    'glow_edge': self.trace_glow_checkbox.isChecked(),
                    'blink_mode': self.trace_blink_combo.currentText(),
                }
            )
            row = self._legend_rows.get(signal_id)
            if row is not None:
                row.setText(2, '2nd' if state.style.get('axis_assignment') == 'secondary' else '1st')
            if state.style.get('axis_assignment') == 'secondary':
                self.statusBar().showMessage('Secondary axis is still preview-only; line and marker styling updates are live.', 3500)
            self._rerender_trace(signal_id)
            self._save_trace_styles()


        def _reset_active_trace_style(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None:
                return
            self._trace_states[signal_id].style = self._initial_style_for_signal(signal_id)
            self._sync_trace_inspector()
            self._rerender_trace(signal_id)
            self._save_trace_styles()

        def _choose_trace_color(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None or signal_id not in self._trace_states:
                return
            color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._trace_states[signal_id].style.get('color', '#5dade2')), self)
            if not color.isValid():
                return
            self.trace_color_button.setText(color.name())
            self._apply_trace_style_from_controls()

        def _on_lens_changed(self) -> None:
            self.selected_lens_id = self.signal_lens_combo.currentData()
            self.settings.setValue('ui/selected_lens_id', self.selected_lens_id)
            self._refresh_signal_inventory()
            for row in self._legend_rows.values():
                signal_id = row.data(0, QtCore.Qt.UserRole)
                row.setText(0, self._label_for_signal(signal_id))

        def _add_selected_signals(self) -> None:
            for item in self.available_signals_list.selectedItems():
                signal_id = item.data(QtCore.Qt.UserRole)
                self._ensure_trace(signal_id)
            if self.available_signals_list.selectedItems():
                self._set_selected_trace(self.available_signals_list.selectedItems()[0].data(QtCore.Qt.UserRole))

        def _remove_selected_trace(self) -> None:
            signal_id = self._active_signal_id
            if signal_id is None:
                return
            state = self._trace_states.pop(signal_id, None)
            if state is None:
                return
            self.plot_widget.removeItem(state.main_item)
            self.plot_widget.removeItem(state.overlay_item)
            row = self._legend_rows.pop(signal_id, None)
            if row is not None:
                index = self.legend_tree.indexOfTopLevelItem(row)
                if index >= 0:
                    self.legend_tree.takeTopLevelItem(index)
            self._active_signal_id = None
            if self._trace_states:
                self._set_selected_trace(next(iter(self._trace_states.keys())))
            self._save_settings()

        def _on_legend_selection_changed(self) -> None:
            item = self.legend_tree.currentItem()
            if item is None:
                return
            signal_id = item.data(0, QtCore.Qt.UserRole)
            self._set_selected_trace(signal_id)

        def _on_legend_item_changed(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
            if column != 0:
                return
            signal_id = item.data(0, QtCore.Qt.UserRole)
            state = self._trace_states.get(signal_id)
            if state is None:
                return
            state.visible = item.checkState(0) == QtCore.Qt.Checked
            self._save_settings()

        def _add_note(self) -> None:
            text = self.note_entry.toPlainText().strip()
            if not text:
                return
            entry = f't+{self.runtime.snapshot().elapsed_seconds:0.1f}s — {text}'
            self._notes.append(entry)
            self.note_list.addItem(entry)
            self.note_entry.clear()
            self._refresh_session_review(self.runtime.snapshot())
            self._refresh_system_summary()

        def _review_detail_text(self, item_text: str) -> str:
            snapshot = self.runtime.snapshot()
            scenario_or_device = snapshot.scenario.display_name if self.runtime_mode != 'LIVE' else snapshot.device_label
            return '\n'.join(
                [
                    f'Review Item: {item_text}',
                    f'Runtime: {self.runtime_mode}',
                    f'Context: {scenario_or_device}',
                    f'Elapsed: {snapshot.elapsed_seconds:0.2f} s',
                    f'Notes: {len(self._notes)}',
                    f'Active traces: {len(self._trace_states)}',
                ] + list(snapshot.event_log[-6:])
            )


        def _refresh_session_review(self, snapshot: Any) -> None:
            current = self.session_review_list.currentItem().text() if self.session_review_list.currentItem() else 'Current demo session'
            self.session_review_detail.setPlainText(self._review_detail_text(current))

        def _refresh_diagnostics(self, snapshot: Any) -> None:
            capability = self._selected_capability_record()
            payload = {
                'runtime_mode': self.runtime_mode,
                'scenario_or_device': snapshot.scenario.display_name if self.runtime_mode != 'LIVE' else snapshot.device_label,
                'connection_state': 'connected' if self.runtime_mode != 'LIVE' else snapshot.connection_state,
                'signal_count': len(snapshot.signal_snapshots),
                'active_trace_count': len(self._trace_states),
                'selected_lens_id': self.selected_lens_id,
                'selected_trace_id': self._active_signal_id,
                'active_workspace': self.selected_workspace_id,
                'graph_mode': self._graph_presentation,
                'autosave_enabled': self.autosave_enabled,
                'control_posture': self.control_posture,
                'outer_splitter_sizes': list(self.outer_splitter.sizes()),
                'center_splitter_sizes': list(self.center_splitter.sizes()),
                'window_geometry': serialize_rect(self._qt_rect_to_policy_rect(self.geometry())),
                'pip_rect': None if self._pip_rect is None else serialize_rect(self._pip_rect),
                'menu_bar': [menu.label for menu in self.spec.menus],
                'notes': len(self._notes),
                'selected_device_capability': None if capability is None else {
                    'device_key': capability.device_key,
                    'capability_mode': capability.capability_mode,
                    'identity_state': capability.identity_state,
                    'read_state': capability.read_state,
                    'write_state': capability.write_state,
                    'limited_access_reason': capability.limited_access_reason,
                },
                'live_runtime_inventory': self.live_runtime.inventory(),
                'guarded_action': self._last_guard_decision if isinstance(self._last_guard_decision, dict) else None if self._last_guard_decision is None else {
                    'allowed': self._last_guard_decision.allowed,
                    'reason': self._last_guard_decision.reason,
                    'target_class': self._last_guard_decision.target_class,
                    'point_id': self._last_guard_decision.point_id,
                    'request_value': self._last_guard_decision.request_value,
                    'runtime_mode': self._last_guard_decision.runtime_mode,
                    'posture': self._last_guard_decision.posture,
                },
            }
            self.diagnostics_text.setPlainText(json.dumps(payload, indent=2, sort_keys=True))


        def _default_logic_nodes(self) -> list[dict[str, Any]]:
            return [
                {'node_id': 'logic-source-1', 'type': 'Source', 'label': 'Selected Signal Source', 'source_signal_id': ''},
                {'node_id': 'logic-math-1', 'type': 'Math', 'label': 'Scale + Offset', 'scale': 1.0, 'offset': 0.0},
                {'node_id': 'logic-comparator-1', 'type': 'Comparator', 'label': '> Threshold', 'operator': '>', 'threshold': 2.0},
                {'node_id': 'logic-sink-1', 'type': 'Sink', 'label': 'Draft Internal Variable', 'target': 'draft_internal_variable'},
            ]

        def _reset_logic_nodes(self) -> None:
            self._logic_nodes = self._default_logic_nodes()
            self._logic_last_outputs.clear()
            self._build_logic_demo_scene()
            self._refresh_logic_watch(self.runtime.snapshot())
            self.statusBar().showMessage('Reset draft logic chain to the default demo model', 2500)

        def _add_logic_node(self, node_type: str) -> None:
            node_type = str(node_type or 'Source')
            next_index = len(self._logic_nodes) + 1
            node = {'node_id': f'logic-{node_type.lower()}-{next_index}', 'type': node_type, 'label': node_type}
            if node_type == 'Source':
                node['source_signal_id'] = self._active_signal_id or ''
                node['label'] = 'Tagged / Selected Source'
            elif node_type == 'Filter':
                node.update({'label': 'Low-pass Filter', 'filter_kind': 'low_pass', 'alpha': 0.45})
            elif node_type == 'Math':
                node.update({'label': 'Scale + Offset', 'scale': 1.0, 'offset': 0.0})
            elif node_type == 'Comparator':
                node.update({'label': '> Threshold', 'operator': '>', 'threshold': 2.0})
            elif node_type == 'Sink':
                node.update({'label': 'Draft Sink', 'target': f'draft_sink_{next_index}'})
            self._logic_nodes.append(node)
            self._build_logic_demo_scene()
            self._refresh_logic_watch(self.runtime.snapshot())
            self.statusBar().showMessage(f'Added draft logic node: {node_type}', 2500)

        def _remove_last_logic_node(self) -> None:
            if not self._logic_nodes:
                self._build_logic_demo_scene()
                self._refresh_logic_watch(self.runtime.snapshot())
                self.statusBar().showMessage('No draft logic nodes are available to remove', 2500)
                return
            removed = self._logic_nodes.pop()
            self._logic_last_outputs.pop(str(removed.get('node_id', '')), None)
            self._build_logic_demo_scene()
            self._refresh_logic_watch(self.runtime.snapshot())
            self.statusBar().showMessage(f"Removed draft logic node: {removed.get('label', removed.get('type', 'node'))}", 2500)

        def _evaluate_logic_nodes(self, snapshot: Any) -> list[dict[str, Any]]:
            signal_map = {item.descriptor.signal_id: item for item in snapshot.signal_snapshots}
            rows: list[dict[str, Any]] = []
            current_value = 0.0
            current_label = 'unset'
            for node in self._logic_nodes:
                node_type = str(node.get('type', 'Source'))
                if node_type == 'Source':
                    signal_id = str(node.get('source_signal_id') or self._active_signal_id or (next(iter(signal_map)) if signal_map else ''))
                    snapshot_row = signal_map.get(signal_id)
                    current_value = 0.0 if snapshot_row is None else float(snapshot_row.value)
                    current_label = self._label_for_signal(signal_id) if signal_id else 'No signal selected'
                    node['source_signal_id'] = signal_id
                    output_text = f'{current_value:0.3f}'
                    detail = current_label
                elif node_type == 'Filter':
                    filter_kind = str(node.get('filter_kind', 'low_pass'))
                    alpha = float(node.get('alpha', 0.45))
                    if filter_kind == 'low_pass':
                        previous = float(self._logic_last_outputs.get(node['node_id'], current_value))
                        current_value = previous + alpha * (current_value - previous)
                        detail = f'low_pass α={alpha:0.2f}'
                    else:
                        detail = filter_kind
                    output_text = f'{current_value:0.3f}'
                elif node_type == 'Math':
                    scale = float(node.get('scale', 1.0))
                    offset = float(node.get('offset', 0.0))
                    current_value = current_value * scale + offset
                    detail = f'scale={scale:0.2f}, offset={offset:0.2f}'
                    output_text = f'{current_value:0.3f}'
                elif node_type == 'Comparator':
                    operator = str(node.get('operator', '>'))
                    threshold = float(node.get('threshold', 2.0))
                    if operator == '<':
                        current_value = 1.0 if current_value < threshold else 0.0
                    elif operator == '==':
                        current_value = 1.0 if abs(current_value - threshold) <= 1e-9 else 0.0
                    else:
                        current_value = 1.0 if current_value > threshold else 0.0
                    detail = f'{operator} {threshold:0.2f}'
                    output_text = 'true' if current_value > 0.5 else 'false'
                elif node_type == 'Sink':
                    target = str(node.get('target', 'draft_sink'))
                    detail = f'draft target: {target}'
                    output_text = f'{current_value:0.3f}'
                else:
                    detail = 'passthrough'
                    output_text = f'{current_value:0.3f}'
                self._logic_last_outputs[str(node.get('node_id', node_type))] = current_value
                rows.append({'label': str(node.get('label', node_type)), 'type': node_type, 'detail': detail, 'output': output_text})
            return rows

        def _refresh_logic_watch(self, snapshot: Any) -> None:
            rows = self._evaluate_logic_nodes(snapshot)
            self.logic_inspector.clear()
            lines = [
                f'Logic draft state: {self.runtime_mode} / simulated authoring surface',
                'Authority: draft / simulated only — not deployed to runtime control and not permitted to write hardware.',
            ]
            if not rows:
                lines.append('No draft logic nodes are currently defined. Use Add Draft Node or Reset Draft Chain.')
            for row in rows:
                lines.append(f"{row['type']}: {row['label']} | {row['detail']} | output {row['output']}")
                parent = QtWidgets.QTreeWidgetItem(self.logic_inspector, [row['label'], row['output']])
                QtWidgets.QTreeWidgetItem(parent, ['Type', row['type']])
                QtWidgets.QTreeWidgetItem(parent, ['Detail', row['detail']])
            self.logic_inspector.expandAll()
            self.logic_watch.setPlainText('\n'.join(lines))

        def _build_logic_demo_scene(self) -> None:
            self.logic_scene.clear()
            if not self._logic_nodes:
                notice = self.logic_scene.addText('No draft logic nodes')
                notice.setDefaultTextColor(QtGui.QColor('#f5f7fa'))
                notice.setPos(24, 48)
                return
            x = 20
            y = 40
            box_w = 180
            box_h = 92
            gap = 48
            for node in self._logic_nodes:
                label = str(node.get('label', node.get('type', 'Node')))
                node_type = str(node.get('type', 'Node'))
                detail = ''
                if node_type == 'Source':
                    detail = self._label_for_signal(str(node.get('source_signal_id') or self._active_signal_id or ''))
                elif node_type == 'Math':
                    detail = f"scale {float(node.get('scale', 1.0)):0.2f} / offset {float(node.get('offset', 0.0)):0.2f}"
                elif node_type == 'Comparator':
                    detail = f"{node.get('operator', '>')} {float(node.get('threshold', 2.0)):0.2f}"
                elif node_type == 'Filter':
                    detail = f"{node.get('filter_kind', 'low_pass')} α={float(node.get('alpha', 0.45)):0.2f}"
                elif node_type == 'Sink':
                    detail = str(node.get('target', 'draft_sink'))
                rect = self.logic_scene.addRect(x, y, box_w, box_h, pen=QtGui.QPen(QtGui.QColor('#6ea8fe'), 2), brush=QtGui.QBrush(QtGui.QColor('#1f2933')))
                title = self.logic_scene.addText(label)
                title.setDefaultTextColor(QtGui.QColor('#f5f7fa'))
                title.setPos(x + 12, y + 12)
                subtitle = self.logic_scene.addText(f'{node_type} — {detail}')
                subtitle.setDefaultTextColor(QtGui.QColor('#cbd5e1'))
                subtitle.setPos(x + 12, y + 46)
                _ = rect
                if x > 20:
                    self.logic_scene.addLine(x - gap + 16, y + box_h / 2, x, y + box_h / 2, pen=QtGui.QPen(QtGui.QColor('#7f8c8d'), 2, QtCore.Qt.DashLine))
                x += box_w + gap

        def resizeEvent(self, event: Any) -> None:
            super().resizeEvent(event)
            if hasattr(self, 'pip_overlay'):
                QtCore.QTimer.singleShot(0, self._clamp_and_commit_pip_geometry)

        def _workspace_bounds_rect(self) -> Rect:
            if not hasattr(self, 'workspace_host'):
                return Rect(x=0, y=0, width=800, height=600)
            local = self.workspace_host.rect()
            return Rect(x=0, y=0, width=max(320, local.width()), height=max(220, local.height()))

        def _position_pip_overlay_default(self, *, force: bool = False) -> None:
            if not hasattr(self, 'pip_overlay'):
                return
            bounds = self._workspace_bounds_rect()
            mode = self._graph_presentation if self._graph_presentation in {'primary', 'compact_pip'} else 'compact_pip'
            target = default_pip_rect(bounds=bounds, mode=mode)
            if force or self._pip_rect is None:
                self._pip_rect = target
            else:
                self._pip_rect = clamp_pip_rect(requested=self._pip_rect, bounds=bounds).resolved
            self.pip_overlay.setGeometry(self._pip_rect.x, self._pip_rect.y, self._pip_rect.width, self._pip_rect.height)
            self.pip_overlay.raise_()

        def _clamp_and_commit_pip_geometry(self) -> None:
            if not hasattr(self, 'pip_overlay') or not self.pip_overlay.isVisible():
                return
            bounds = self._workspace_bounds_rect()
            requested = Rect(
                x=self.pip_overlay.x(),
                y=self.pip_overlay.y(),
                width=self.pip_overlay.width(),
                height=self.pip_overlay.height(),
            )
            self._pip_rect = clamp_pip_rect(requested=requested, bounds=bounds).resolved
            self.pip_overlay.setGeometry(self._pip_rect.x, self._pip_rect.y, self._pip_rect.width, self._pip_rect.height)

        def _apply_graph_presentation(self, mode: str, *, persist: bool = True) -> None:
            mode = mode if mode in {'primary', 'compact_pip', 'hidden'} else 'compact_pip'
            previous_mode = getattr(self, '_graph_presentation', None)
            self._graph_presentation = mode
            if hasattr(self, 'pip_overlay'):
                if self.selected_workspace_id == 'operate':
                    self.pip_overlay.hide()
                elif mode == 'hidden':
                    self.pip_overlay.hide()
                else:
                    if self._pip_rect is None or previous_mode != mode:
                        self._pip_rect = default_pip_rect(bounds=self._workspace_bounds_rect(), mode=mode)
                    self._position_pip_overlay_default(force=True)
                    self.pip_overlay.show()
                    self.pip_overlay.raise_()
            graph_text = {'primary': 'Primary', 'compact_pip': 'PiP', 'hidden': 'Hidden'}.get(mode, mode.replace('_', ' '))
            self._top_bar_labels['graph'].setText(graph_text)
            if hasattr(self._top_bar_labels['graph'], 'setToolTip'):
                self._top_bar_labels['graph'].setToolTip('Graph presentation mode — click to switch between Primary, PiP, and Hidden states')
            self._refresh_top_bar_semantics()
            if persist and self._ui_built:
                self._save_settings()

        def _toggle_graph_primary_overlay(self) -> None:
            if self.selected_workspace_id == 'operate':
                return
            next_mode = 'compact_pip' if self._graph_presentation == 'primary' else 'primary'
            self._graph_presentation_override = next_mode
            self._apply_graph_presentation(next_mode)

        def _hide_graph_overlay(self) -> None:
            self._graph_presentation_override = 'hidden'
            self._apply_graph_presentation('hidden')

        def _render_pip_overlay(self, snapshot: Any) -> None:
            if not hasattr(self, 'pip_overlay') or not self.pip_overlay.isVisible():
                return
            self.pip_overlay.plot_widget.clear()
            visible_signal_ids = [signal_id for signal_id, state in self._trace_states.items() if state.visible]
            chosen = visible_signal_ids[:3]
            if self._active_signal_id in visible_signal_ids:
                chosen = [self._active_signal_id] + [sid for sid in visible_signal_ids if sid != self._active_signal_id][:2]
            self.pip_overlay.title_label.setText(f'Graph — {self._graph_presentation.replace('_', ' ')}')
            for signal_id in chosen:
                state = self._trace_states.get(signal_id)
                if state is None:
                    continue
                series = self.runtime.trace_series(signal_id)
                if not series.x_values:
                    continue
                self.pip_overlay.plot_widget.plot(series.x_values, series.y_values, pen=_pen_from_style(pg, QtCore, state.style))

        def _apply_workspace_selection(self, workspace_id: str) -> None:
            lookup = {workspace.workspace_id: index for index, workspace in enumerate(self.spec.workspaces)}
            if workspace_id in lookup:
                self.workspace_tabs.setCurrentIndex(lookup[workspace_id])
                self.selected_workspace_id = workspace_id
                self.settings.setValue('ui/selected_workspace', workspace_id)
            if workspace_id == 'operate':
                self.explorer_tabs.setCurrentIndex(self.explorer_tab_indexes['signal'])
                self.control_tabs.setCurrentIndex(self.control_tab_indexes['session'])
            elif workspace_id == 'logic_designer':
                self.explorer_tabs.setCurrentIndex(self.explorer_tab_indexes['signal'])
                self.control_tabs.setCurrentIndex(self.control_tab_indexes['signals'])
            elif workspace_id == 'system':
                self.explorer_tabs.setCurrentIndex(self.explorer_tab_indexes['device'])
                self.control_tabs.setCurrentIndex(self.control_tab_indexes['diagnostics'])
            elif workspace_id == 'session_review':
                self.control_tabs.setCurrentIndex(self.control_tab_indexes['notes'])
            for workspace in self.spec.workspaces:
                action = self._menu_actions.get(f'workspace_{workspace.workspace_id}')
                if action is not None:
                    action.setChecked(workspace.workspace_id == workspace_id)
            mode = self._graph_presentation_override or default_graph_presentation_for_workspace(workspace_id)
            self._apply_graph_presentation(mode, persist=False)
            self._refresh_capability_summary()
            self._refresh_system_summary()

        def _on_workspace_tab_changed(self, index: int) -> None:
            workspace_id = self.spec.workspaces[index].workspace_id
            self.selected_workspace_id = workspace_id
            self.settings.setValue('ui/selected_workspace', workspace_id)
            for workspace in self.spec.workspaces:
                action = self._menu_actions.get(f'workspace_{workspace.workspace_id}')
                if action is not None:
                    action.setChecked(workspace.workspace_id == workspace_id)
            mode = self._graph_presentation_override or default_graph_presentation_for_workspace(workspace_id)
            self._apply_graph_presentation(mode, persist=False)
            self._refresh_capability_summary()
            self._refresh_system_summary()

        def _toggle_control_dock(self) -> None:
            self.control_dock.setVisible(not self.control_dock.isVisible())
            self._menu_actions['view_toggle_control_dock'].setChecked(self.control_dock.isVisible())

        def _toggle_bottom_dock(self) -> None:
            self.bottom_dock.setVisible(not self.bottom_dock.isVisible())
            self._menu_actions['view_toggle_bottom_log'].setChecked(self.bottom_dock.isVisible())

        def _toggle_device_explorer_tab(self) -> None:
            visible = not self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['device'])
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['device'], visible)
            self._menu_actions['view_toggle_device_explorer'].setChecked(visible)

        def _toggle_signal_explorer_tab(self) -> None:
            visible = not self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['signal'])
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['signal'], visible)
            self._menu_actions['view_toggle_signal_explorer'].setChecked(visible)

        def _toggle_trace_inspector_tab(self) -> None:
            visible = not self.control_tabs.isTabVisible(self.control_tab_indexes['trace'])
            self.control_tabs.setTabVisible(self.control_tab_indexes['trace'], visible)
            self._menu_actions['view_toggle_trace_inspector'].setChecked(visible)

        def _toggle_notes_tab(self) -> None:
            visible = not self.control_tabs.isTabVisible(self.control_tab_indexes['notes'])
            self.control_tabs.setTabVisible(self.control_tab_indexes['notes'], visible)
            self._menu_actions['view_toggle_notes'].setChecked(visible)

        def _reset_panel_sizes(self) -> None:
            total_width = max(1200, self.outer_splitter.size().width() or self.width() or 1600)
            total_height = max(700, self.center_splitter.size().height() or self.height() or 900)
            outer = normalize_splitter_sizes(total=total_width, requested=(280, 1040, 320), minimums=(210, 760, 240))
            center = normalize_splitter_sizes(total=total_height, requested=(760, 220), minimums=(420, 150))
            self.outer_splitter.setSizes(list(outer))
            self.center_splitter.setSizes(list(center))
            if hasattr(self, 'operate_splitter'):
                self.operate_splitter.setSizes([max(760, int(total_width * 0.78)), max(180, int(total_width * 0.18))])
            if hasattr(self, 'logic_splitter'):
                self.logic_splitter.setSizes([190, 760, 250])
            self._position_pip_overlay_default(force=True)
            self.statusBar().showMessage('Panel sizes reset to workspace defaults', 2000)

        def _restore_default_layout(self) -> None:
            self.control_dock.setVisible(True)
            self.bottom_dock.setVisible(True)
            self.explorer_dock.setVisible(True)
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['device'], True)
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['signal'], True)
            self.control_tabs.setTabVisible(self.control_tab_indexes['trace'], True)
            self.control_tabs.setTabVisible(self.control_tab_indexes['notes'], True)
            self._menu_actions['view_toggle_control_dock'].setChecked(True)
            self._menu_actions['view_toggle_bottom_log'].setChecked(True)
            self._menu_actions['view_toggle_device_explorer'].setChecked(True)
            self._menu_actions['view_toggle_signal_explorer'].setChecked(True)
            self._menu_actions['view_toggle_trace_inspector'].setChecked(True)
            self._menu_actions['view_toggle_notes'].setChecked(True)
            self._graph_presentation_override = None
            self._apply_graph_presentation(default_graph_presentation_for_workspace(self.selected_workspace_id), persist=False)
            self._reset_panel_sizes()

        def _on_demo_scenario_changed(self) -> None:
            scenario_id = self.demo_scenario_combo.currentData()
            self.demo_runtime.activate_scenario(scenario_id)
            self.settings.setValue('ui/active_scenario_id', scenario_id)
            for item in list(self._trace_states.values()):
                self.plot_widget.removeItem(item.main_item)
                self.plot_widget.removeItem(item.overlay_item)
            self._trace_states.clear()
            self._legend_rows.clear()
            self.legend_tree.clear()
            self._refresh_signal_inventory()
            self._ensure_default_trace_selection()
            self._build_logic_demo_scene()
            self._render_step()

        def _connect_live_device(self) -> None:
            device_key = self._selected_live_device_key()
            if not device_key:
                self.statusBar().showMessage('No live device is available to connect', 2500)
                return
            success = self.live_runtime.connect(device_key=device_key)
            if success:
                self.statusBar().showMessage(f'Connected live device: {device_key}', 2500)
                if self.runtime_mode == 'LIVE':
                    self._switch_runtime_mode('LIVE')
            else:
                self.statusBar().showMessage(f'Connect failed: {device_key}', 3500)
                self._render_step()

        def _disconnect_live_device(self) -> None:
            self.live_runtime.disconnect()
            if self.runtime_mode == 'LIVE':
                self._render_step()
            self.statusBar().showMessage('Live device disconnected', 2500)

        def _set_control_posture(self, posture: str) -> None:
            self.control_posture = posture
            self.control_posture_label.setText(posture)
            self.settings.setValue('runtime/control_posture', posture)
            self.bottom_log.appendPlainText(f'posture changed: {posture}')
            self._render_step()

        def _perform_guarded_write(self) -> None:
            if self.runtime_mode == 'LIVE':
                target = next((item for item in self.live_runtime.writable_targets() if item.point_id == 'analog_out_0'), None)
                if target is None:
                    self.bottom_log.appendPlainText('guarded write unavailable: no live writable DAC0 target')
                    return
                decision = self.live_runtime.request_write(point_id=target.point_id, request_value='2.500', posture=self.control_posture)
                self._last_guard_decision = decision
                self.bottom_log.appendPlainText(f'guarded write ({decision.runtime_mode}/{decision.posture}): {decision.point_id} -> {decision.request_value} / allowed={decision.allowed} / reason={decision.reason or "ok"}')
            else:
                allowed = self.control_posture == 'armed_control'
                reason = 'demo_only_simulated' if allowed else 'control posture does not permit demo writes'
                self._last_guard_decision = {'allowed': allowed, 'reason': reason, 'runtime_mode': 'USER-DEMO', 'posture': self.control_posture}
                self.bottom_log.appendPlainText(f'guarded demo write: allowed={allowed} / reason={reason}')
            self._refresh_diagnostics(self.runtime.snapshot())

        def _ensure_demo_mode(self) -> None:
            self._switch_runtime_mode('USER-DEMO')
            self.statusBar().showMessage('User-Demo mode active', 2000)

        def _ensure_live_mode(self) -> None:
            self._switch_runtime_mode('LIVE')
            self.statusBar().showMessage('Live runtime mode active', 2000)

        def _save_graph_setup_interactive(self) -> None:
            name, ok = QtWidgets.QInputDialog.getText(self, 'Save Graph Setup', 'Graph setup name:')
            if not ok or not name.strip():
                return
            payload = {
                'selected_lens_id': self.selected_lens_id,
                'active_traces': list(self._trace_states.keys()),
                'selected_trace_id': self._active_signal_id,
                'trace_styles': {signal_id: state.style for signal_id, state in self._trace_states.items()},
            }
            self._graph_setups[name.strip()] = payload
            self.settings.setValue('graph_setups/json', json.dumps(self._graph_setups, sort_keys=True))
            self.statusBar().showMessage(f'Saved graph setup: {name.strip()}', 2500)

        def _load_graph_setup_interactive(self) -> None:
            if not self._graph_setups:
                QtWidgets.QMessageBox.information(self, 'Load Graph Setup', 'No saved graph setups are available yet.')
                return
            name, ok = QtWidgets.QInputDialog.getItem(self, 'Load Graph Setup', 'Choose setup:', sorted(self._graph_setups.keys()), editable=False)
            if not ok or not name:
                return
            payload = self._graph_setups[name]
            self.selected_lens_id = payload.get('selected_lens_id', 'logical')
            idx = self.signal_lens_combo.findData(self.selected_lens_id)
            if idx >= 0:
                self.signal_lens_combo.setCurrentIndex(idx)
            for item in list(self._trace_states.values()):
                self.plot_widget.removeItem(item.main_item)
                self.plot_widget.removeItem(item.overlay_item)
            self._trace_states.clear()
            self._legend_rows.clear()
            self.legend_tree.clear()
            for signal_id in payload.get('active_traces', []):
                self._ensure_trace(signal_id)
                style = payload.get('trace_styles', {}).get(signal_id)
                if isinstance(style, dict):
                    self._trace_states[signal_id].style.update(style)
            selected_trace = payload.get('selected_trace_id')
            if selected_trace in self._trace_states:
                self._set_selected_trace(selected_trace)
            self._save_trace_styles()
            self.statusBar().showMessage(f'Loaded graph setup: {name}', 2500)


        def _capture_shell_view_payload(self) -> dict[str, Any]:
            return {
                'workspace_id': self.selected_workspace_id,
                'explorer_tab_index': self.explorer_tabs.currentIndex(),
                'control_tab_index': self.control_tabs.currentIndex(),
                'device_explorer_visible': self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['device']),
                'signal_explorer_visible': self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['signal']),
                'trace_inspector_visible': self.control_tabs.isTabVisible(self.control_tab_indexes['trace']),
                'notes_visible': self.control_tabs.isTabVisible(self.control_tab_indexes['notes']),
                'control_dock_visible': self.control_dock.isVisible(),
                'bottom_dock_visible': self.bottom_dock.isVisible(),
                'layout_schema_version': self._layout_schema_version,
                'graph_presentation': self._graph_presentation,
                'graph_presentation_override': self._graph_presentation_override,
                'window_geometry': serialize_rect(self._qt_rect_to_policy_rect(self.geometry())),
                'outer_splitter_sizes': list(self.outer_splitter.sizes()),
                'center_splitter_sizes': list(self.center_splitter.sizes()),
                'pip_rect': None if self._pip_rect is None else serialize_rect(self._pip_rect),
            }

        def _apply_shell_view_payload(self, payload: dict[str, Any]) -> None:
            if int(payload.get('layout_schema_version', self._layout_schema_version)) != self._layout_schema_version:
                self.statusBar().showMessage('Saved view ignored stale layout schema and fell back to current defaults', 3000)
                self._restore_default_layout()
                return
            geometry_payload = deserialize_rect(payload.get('window_geometry'))
            if geometry_payload is not None:
                decision = clamp_window_rect(requested=geometry_payload, available=self._available_policy_rect())
                self._apply_policy_rect(decision.resolved)
            self.control_dock.setVisible(bool(payload.get('control_dock_visible', True)))
            self.bottom_dock.setVisible(bool(payload.get('bottom_dock_visible', True)))
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['device'], bool(payload.get('device_explorer_visible', True)))
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['signal'], bool(payload.get('signal_explorer_visible', True)))
            self.control_tabs.setTabVisible(self.control_tab_indexes['trace'], bool(payload.get('trace_inspector_visible', True)))
            self.control_tabs.setTabVisible(self.control_tab_indexes['notes'], bool(payload.get('notes_visible', True)))
            if isinstance(payload.get('explorer_tab_index'), int):
                self.explorer_tabs.setCurrentIndex(int(payload['explorer_tab_index']))
            if isinstance(payload.get('control_tab_index'), int):
                self.control_tabs.setCurrentIndex(int(payload['control_tab_index']))
            workspace_id = str(payload.get('workspace_id', self.selected_workspace_id))
            self._graph_presentation_override = payload.get('graph_presentation_override')
            self._apply_workspace_selection(workspace_id)
            outer = payload.get('outer_splitter_sizes') or []
            center = payload.get('center_splitter_sizes') or []
            if len(outer) == 3:
                total_width = max(1200, self.outer_splitter.size().width() or self.width() or sum(int(v) for v in outer))
                self.outer_splitter.setSizes(list(normalize_splitter_sizes(total=total_width, requested=tuple(int(v) for v in outer), minimums=(210, 760, 240))))
            if len(center) == 2:
                total_height = max(700, self.center_splitter.size().height() or self.height() or sum(int(v) for v in center))
                self.center_splitter.setSizes(list(normalize_splitter_sizes(total=total_height, requested=tuple(int(v) for v in center), minimums=(420, 150))))
            pip_payload = deserialize_rect(payload.get('pip_rect'))
            if pip_payload is not None:
                self._pip_rect = pip_payload
                self._clamp_and_commit_pip_geometry()
            self._menu_actions['view_toggle_control_dock'].setChecked(self.control_dock.isVisible())
            self._menu_actions['view_toggle_bottom_log'].setChecked(self.bottom_dock.isVisible())
            self._menu_actions['view_toggle_device_explorer'].setChecked(self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['device']))
            self._menu_actions['view_toggle_signal_explorer'].setChecked(self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['signal']))
            self._menu_actions['view_toggle_trace_inspector'].setChecked(self.control_tabs.isTabVisible(self.control_tab_indexes['trace']))
            self._menu_actions['view_toggle_notes'].setChecked(self.control_tabs.isTabVisible(self.control_tab_indexes['notes']))

        def _save_current_view_interactive(self) -> None:
            name, ok = QtWidgets.QInputDialog.getText(self, 'Save Current View', 'View name:')
            if not ok or not name.strip():
                return
            payload = self._capture_shell_view_payload()
            custom = json.loads(self._saved_views.to_json()) if self._saved_views.custom_names else {'custom_views': []}
            custom_views = [row for row in custom.get('custom_views', []) if row.get('name') != name.strip()]
            custom_views.append({'name': name.strip(), 'built_in': False, 'snapshot': {'workspace_id': self.selected_workspace_id}, 'payload': payload})
            serialized = json.dumps({'custom_views': custom_views}, indent=2, sort_keys=True)
            self.settings.setValue('ui/saved_views_json', serialized)
            self._saved_views = ShellViewCatalog.from_json(serialized)
            self.statusBar().showMessage(f'Saved view: {name.strip()}', 2500)

        def _manage_saved_views_interactive(self) -> None:
            raw = self.settings.value('ui/saved_views_json', '', type=str)
            try:
                payload = json.loads(raw) if raw else {'custom_views': []}
            except json.JSONDecodeError:
                payload = {'custom_views': []}
            names = list(self._saved_views.built_in_names) + [row.get('name', 'Unnamed View') for row in payload.get('custom_views', [])]
            if not names:
                QtWidgets.QMessageBox.information(self, 'Manage Saved Views', 'No saved views are available yet.')
                return
            name, ok = QtWidgets.QInputDialog.getItem(self, 'Manage Saved Views', 'Choose a view to load or delete:', names, editable=False)
            if not ok or not name:
                return
            built_in = self._saved_views.get(name)
            if built_in is not None and built_in.built_in:
                self._apply_workspace_selection(built_in.snapshot.workspace_id)
                self._reset_panel_sizes()
                self.statusBar().showMessage(f'Loaded built-in view: {name}', 2500)
                return
            selected_row = next((row for row in payload.get('custom_views', []) if row.get('name') == name), None)
            if selected_row is None:
                return
            choice = QtWidgets.QMessageBox.question(
                self,
                'Manage Saved Views',
                f'Load or delete saved view "{name}"?',
                QtWidgets.QMessageBox.Open | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Open,
            )
            if choice == QtWidgets.QMessageBox.Discard:
                payload['custom_views'] = [row for row in payload.get('custom_views', []) if row.get('name') != name]
                serialized = json.dumps(payload, indent=2, sort_keys=True)
                self.settings.setValue('ui/saved_views_json', serialized)
                self._saved_views = ShellViewCatalog.from_json(serialized)
                self.statusBar().showMessage(f'Deleted saved view: {name}', 2500)
                return
            if choice != QtWidgets.QMessageBox.Open:
                return
            self._apply_shell_view_payload(selected_row.get('payload', {}))
            self.statusBar().showMessage(f'Loaded saved view: {name}', 2500)

        def _load_graph_setups(self) -> dict[str, dict[str, Any]]:
            raw = self.settings.value('graph_setups/json', '', type=str)
            if not raw:
                return {}
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return {str(key): dict(value) for key, value in payload.items() if isinstance(value, dict)}

        def _load_tag_names(self) -> dict[str, str]:
            raw = self.settings.value('ui/tag_names_json', '', type=str)
            if not raw:
                return {}
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return {str(key): str(value) for key, value in payload.items()}

        def _save_tag_names(self) -> None:
            self.settings.setValue('ui/tag_names_json', json.dumps(self._tag_names_by_signal, indent=2, sort_keys=True))

        def _current_device_context(self) -> tuple[str, str]:
            if self.runtime_mode == 'LIVE':
                record = self._selected_capability_record()
                if record is not None:
                    return record.device_key, record.display_name
                key = self._selected_live_device_key()
                if key:
                    return str(key), str(key)
                return 'live::unselected', 'No live device selected'
            snapshot = self.demo_runtime.snapshot()
            scenario = getattr(snapshot, 'scenario', None)
            scenario_id = getattr(scenario, 'scenario_id', self.demo_runtime.active_scenario_id)
            scenario_name = getattr(scenario, 'display_name', 'Demo Scenario')
            return f'demo::{scenario_id}', str(scenario_name)

        def _open_preferences(self) -> None:
            dialog = PreferencesDialog(self)
            dialog.exec()

        def _toggle_autosave_from_menu(self) -> None:
            self.autosave_enabled = self._menu_actions['settings_autosave_toggle'].isChecked()
            self._configure_autosave_timer()
            self._save_settings()

        def _show_about(self) -> None:
            QtWidgets.QMessageBox.information(
                self,
                'About UniversalDAQ',
                'UniversalDAQ\nVisible Operator Shell and Demo Embodiment\nGraph engine: pyqtgraph\nRuntime posture: User-Demo',
            )

        def _show_demo_guide(self) -> None:
            lines = ['User-Demo scenarios:']
            for scenario in self.runtime.available_scenarios():
                lines.append(f'• {scenario.display_name}: {scenario.description}')
            QtWidgets.QMessageBox.information(self, 'User-Demo Guide', '\n'.join(lines))

        def _export_diagnostics(self) -> None:
            default_path = str(self._diagnostics_path or (Path.home() / 'universaldaq_user_demo_diagnostics.json'))
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Export Diagnostics', default_path, 'JSON Files (*.json)')
            if not path:
                return
            snapshot = self.runtime.snapshot()
            self._write_diagnostics_payload(Path(path), snapshot=snapshot)
            self.statusBar().showMessage(f'Exported diagnostics: {path}', 3000)


        def _export_lightweight_report(self) -> None:
            default_path = str(Path.home() / 'universaldaq_demo_session_report.md')
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Export Lightweight Session Report', default_path, 'Markdown Files (*.md)')
            if not path:
                return
            snapshot = self.runtime.snapshot()
            lines = [
                '# UniversalDAQ Lightweight Session Report',
                '',
                f'- Runtime mode: USER-DEMO',
                f'- Scenario: {snapshot.scenario.display_name}',
                f'- Workspace: {self.selected_workspace_id}',
                f'- Active lens: {self.selected_lens_id}',
                f'- Active trace count: {len(self._trace_states)}',
                f'- Active trace: {self._label_for_signal(self._active_signal_id) if self._active_signal_id else "none"}',
                f'- Notes: {len(self._notes)}',
                '',
                '## Recent Events',
            ]
            lines.extend(f'- {item}' for item in snapshot.event_log[-8:])
            lines.append('')
            lines.append('## Operator Notes')
            if self._notes:
                lines.extend(f'- {item}' for item in self._notes)
            else:
                lines.append('- none')
            Path(path).write_text('\n'.join(lines) + '\n', encoding='utf-8')
            self.statusBar().showMessage(f'Exported session report: {path}', 3000)

        def _refresh_system_summary(self) -> None:
            if self._mapping_rows:
                total_count = len(self._mapping_rows)
                mapped_count = sum(1 for row in self._mapping_rows.values() if row['status'] == 'mapped')
                output_count = sum(1 for row in self._mapping_rows.values() if row['direction'] == 'internal_signal_to_device_output')
                unmapped_count = sum(1 for row in self._mapping_rows.values() if row['status'] == 'unmapped')
                invalid_count = sum(1 for row in self._mapping_rows.values() if row['status'] in {'invalid', 'missing_destination', 'missing_source'})
                mapping_summary = type('MappingSummaryRow', (), {
                    'total_count': total_count,
                    'mapped_count': mapped_count,
                    'output_count': output_count,
                    'unmapped_count': unmapped_count,
                    'invalid_count': invalid_count,
                })()
            else:
                mapping_summary = summarize_mapping_rows(build_mapping_rows(
                    signal_descriptors=self.runtime.signal_descriptors(lens_id=self.selected_lens_id),
                    writable_targets=getattr(self.runtime, 'writable_targets', lambda: ())(),
                    runtime_mode=self.runtime_mode,
                ))
            device_summary = summarize_device_io_rows(
                build_device_io_rows(
                    device_context_key=self._selected_device_context_key or self._current_device_context()[0],
                    signal_descriptors=self.runtime.signal_descriptors(lens_id=self.selected_lens_id),
                    mapping_rows=build_mapping_rows(
                        signal_descriptors=self.runtime.signal_descriptors(lens_id=self.selected_lens_id),
                        writable_targets=getattr(self.runtime, 'writable_targets', lambda: ())(),
                        runtime_mode=self.runtime_mode,
                    ),
                    authoritative_rows=self._authoritative_binding_rows,
                    tag_names_by_signal=self._tag_names_by_signal,
                    runtime_mode=self.runtime_mode,
                    health_label=self.runtime.connection_state if self.runtime_mode == 'LIVE' else 'simulated',
                )
            )
            custom_view_count = 0
            raw_saved_views = self.settings.value('ui/saved_views_json', '', type=str)
            if raw_saved_views:
                try:
                    custom_view_count = len(json.loads(raw_saved_views).get('custom_views', []))
                except json.JSONDecodeError:
                    custom_view_count = 0
            self.system_summary.setPlainText(
                '\n'.join(
                    [
                        'UniversalDAQ Visible Operator Shell',
                        f'Active workspace: {self.selected_workspace_id}',
                        f'Runtime mode: {self.runtime_mode}',
                        f'Selected device context: {self._selected_device_context_label}',
                        f'Control posture: {self.control_posture}',
                        f'Autosave enabled: {self.autosave_enabled}',
                        f'Active traces: {len(self._trace_states)}',
                        f'Notes: {len(self._notes)}',
                        f'Device I/O rows: {device_summary.total_count} (inputs {device_summary.input_count}, outputs {device_summary.output_count})',
                        f'Device I/O authority: applied {device_summary.applied_count}, draft {device_summary.draft_count}, unavailable {device_summary.unavailable_count}',
                        f'Mapped rows: {mapping_summary.mapped_count}/{mapping_summary.total_count}',
                        f'Unmapped rows: {mapping_summary.unmapped_count}',
                        f'Output bindings: {mapping_summary.output_count}',
                        f'Custom saved views: {custom_view_count}',
                        f'Authoritative applied binding surface: {self._authoritative_binding_status}',
                        'Persistent top information bar: enabled with semantic state colors',
                        'Graph restore path: top-bar Graph control (Primary / PiP / Hidden)',
                        'Explorer split: Device Explorer = device/raw context, Signal Explorer = internal/tagged signals, System = device I/O inspection and draft mapping',
                    ]
                )
            )
            self._refresh_authoritative_binding_summary()


        def _refresh_authoritative_binding_summary(self) -> None:
            if not hasattr(self, 'authoritative_binding_summary'):
                return
            if self._authoritative_binding_rows:
                lines = [
                    'Authoritative Applied Bindings — backend read model',
                    f'Rows: {len(self._authoritative_binding_rows)}',
                ]
                lines.extend(
                    f"- {row['direction']}: {row['logical_display_name']} -> {row['source_endpoint'] or row['destination_endpoint']} [{row['status']}]"
                    for row in self._authoritative_binding_rows[:8]
                )
            else:
                lines = [
                    'Authoritative Applied Bindings — not attached in the runtime-only visible shell launcher',
                    'Use the controller-backed bridge diagnostics to inspect backend-applied bindings.',
                    'Mapping Drafts below remain non-authoritative until controller-backed apply is implemented.',
                ]
            self.authoritative_binding_summary.setPlainText('\n'.join(lines))

        def _collect_diagnostics_payload(self, snapshot: Any | None = None) -> dict[str, Any]:
            snapshot = self.runtime.snapshot() if snapshot is None else snapshot
            capability = self._selected_capability_record()
            return {
                'shell_title': self.spec.shell_title,
                'runtime_mode': self.runtime_mode,
                'scenario_or_device': snapshot.scenario.display_name if self.runtime_mode != 'LIVE' else snapshot.device_label,
                'active_workspace': self.selected_workspace_id,
                'selected_lens_id': self.selected_lens_id,
                'selected_trace_id': self._active_signal_id,
                'active_trace_count': len(self._trace_states),
                'graph_mode': self._graph_presentation,
                'outer_splitter_sizes': list(self.outer_splitter.sizes()),
                'center_splitter_sizes': list(self.center_splitter.sizes()),
                'window_geometry': serialize_rect(self._qt_rect_to_policy_rect(self.geometry())),
                'available_geometry': serialize_rect(self._available_policy_rect()),
                'pip_rect': None if self._pip_rect is None else serialize_rect(self._pip_rect),
                'menus': [menu.label for menu in self.spec.menus],
                'workspaces': [workspace.label for workspace in self.spec.workspaces],
                'autosave_enabled': self.autosave_enabled,
                'trace_styles': {signal_id: state.style for signal_id, state in self._trace_states.items()},
                'selected_device_capability': None if capability is None else {
                    'device_key': capability.device_key,
                    'capability_mode': capability.capability_mode,
                    'identity_state': capability.identity_state,
                    'read_state': capability.read_state,
                    'write_state': capability.write_state,
                    'limited_access_reason': capability.limited_access_reason,
                },
                'notes': list(self._notes),
                'events': list(snapshot.event_log),
                'saved_view_names': list(self._saved_views.built_in_names),
                'mapping_summary': {
                    'total_count': len(self._mapping_rows),
                    'mapped_count': sum(1 for row in self._mapping_rows.values() if row['status'] == 'mapped'),
                    'output_count': sum(1 for row in self._mapping_rows.values() if row['direction'] == 'internal_signal_to_device_output'),
                    'unmapped_count': sum(1 for row in self._mapping_rows.values() if row['status'] == 'unmapped'),
                },
                'device_io_summary': {
                    'device_context_key': self._selected_device_context_key,
                    'device_context_label': self._selected_device_context_label,
                    'row_count': len(self._device_io_rows),
                    'rows': list(self._device_io_rows[:8]),
                },
                'canonical_tags': dict(self._tag_names_by_signal),
                'authoritative_binding_summary': {
                    'status': self._authoritative_binding_status,
                    'row_count': len(self._authoritative_binding_rows),
                    'rows': list(self._authoritative_binding_rows[:8]),
                },
                'bench_mode': self._bench_mode,
                'bench_runbook_path': self._bench_runbook_path,
                'diagnostics_path': None if self._diagnostics_path is None else str(self._diagnostics_path),
            }

        def _write_diagnostics_payload(self, path: Path, *, snapshot: Any | None = None) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self._collect_diagnostics_payload(snapshot=snapshot), indent=2, sort_keys=True) + '\n', encoding='utf-8')



        def _save_settings(self) -> None:
            self.settings.setValue('ui/selected_lens_id', self.selected_lens_id)
            self.settings.setValue('ui/selected_workspace', self.selected_workspace_id)
            self.settings.setValue('ui/active_scenario_id', self.runtime.active_scenario_id)
            self.settings.setValue('ui/autosave_enabled', self.autosave_enabled)
            self.settings.setValue('ui/autosave_interval_seconds', self.autosave_interval_seconds)
            self.settings.setValue('ui/active_traces', '|'.join(self._trace_states.keys()))
            self.settings.setValue('ui/explorer_current_index', self.explorer_tabs.currentIndex())
            self.settings.setValue('ui/control_current_index', self.control_tabs.currentIndex())
            self.settings.setValue('ui/device_explorer_visible', self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['device']))
            self.settings.setValue('ui/signal_explorer_visible', self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['signal']))
            self.settings.setValue('ui/trace_inspector_visible', self.control_tabs.isTabVisible(self.control_tab_indexes['trace']))
            self.settings.setValue('ui/notes_visible', self.control_tabs.isTabVisible(self.control_tab_indexes['notes']))
            self.settings.setValue('ui/outer_splitter_sizes_json', json.dumps(list(self.outer_splitter.sizes())))
            self.settings.setValue('ui/center_splitter_sizes_json', json.dumps(list(self.center_splitter.sizes())))
            self.settings.setValue('ui/graph_presentation', self._graph_presentation)
            self.settings.setValue('ui/graph_presentation_override', '' if self._graph_presentation_override is None else self._graph_presentation_override)
            self.settings.setValue('ui/pip_rect_json', '' if self._pip_rect is None else json.dumps(serialize_rect(self._pip_rect), sort_keys=True))
            self.settings.setValue('runtime/mode', self.runtime_mode)
            self.settings.setValue('runtime/control_posture', self.control_posture)
            self.settings.setValue('window/layout_schema_version', self._layout_schema_version)
            self.settings.setValue('window/normal_geometry_json', json.dumps(serialize_rect(self._qt_rect_to_policy_rect(self.normalGeometry() if self.isMaximized() else self.geometry())), sort_keys=True))
            self.settings.setValue('window/maximized', self.isMaximized())
            self._save_trace_styles()
            self._save_tag_names()

        def _restore_settings(self) -> None:
            self._restore_window_geometry_from_policy()
            scenario_id = self.settings.value('ui/active_scenario_id', initial_scenario_id, type=str)
            idx = self.demo_scenario_combo.findData(scenario_id)
            if idx >= 0:
                self.demo_scenario_combo.setCurrentIndex(idx)
            self.control_posture = self.settings.value('runtime/control_posture', 'view_only', type=str)
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['device'], self.settings.value('ui/device_explorer_visible', True, type=bool))
            self.explorer_tabs.setTabVisible(self.explorer_tab_indexes['signal'], self.settings.value('ui/signal_explorer_visible', True, type=bool))
            self.control_tabs.setTabVisible(self.control_tab_indexes['trace'], self.settings.value('ui/trace_inspector_visible', True, type=bool))
            self.control_tabs.setTabVisible(self.control_tab_indexes['notes'], self.settings.value('ui/notes_visible', True, type=bool))
            self.explorer_tabs.setCurrentIndex(self.settings.value('ui/explorer_current_index', 1, type=int))
            self.control_tabs.setCurrentIndex(self.settings.value('ui/control_current_index', 0, type=int))
            self._graph_presentation_override = self.settings.value('ui/graph_presentation_override', '', type=str) or None
            raw_pip = self.settings.value('ui/pip_rect_json', '', type=str)
            if raw_pip:
                try:
                    self._pip_rect = deserialize_rect(json.loads(raw_pip))
                except json.JSONDecodeError:
                    self._pip_rect = None
            outer_raw = self.settings.value('ui/outer_splitter_sizes_json', '', type=str)
            center_raw = self.settings.value('ui/center_splitter_sizes_json', '', type=str)
            try:
                outer_sizes = tuple(int(v) for v in json.loads(outer_raw)) if outer_raw else ()
            except json.JSONDecodeError:
                outer_sizes = ()
            try:
                center_sizes = tuple(int(v) for v in json.loads(center_raw)) if center_raw else ()
            except json.JSONDecodeError:
                center_sizes = ()
            if len(outer_sizes) == 3:
                total_width = max(1200, self.width() or sum(outer_sizes))
                self.outer_splitter.setSizes(list(normalize_splitter_sizes(total=total_width, requested=outer_sizes, minimums=(210, 760, 240))))
            if len(center_sizes) == 2:
                total_height = max(700, self.height() or sum(center_sizes))
                self.center_splitter.setSizes(list(normalize_splitter_sizes(total=total_height, requested=center_sizes, minimums=(420, 150))))
            self._sync_mode_menu_checks()
            self._menu_actions['settings_autosave_toggle'].setChecked(self.autosave_enabled)
            self._menu_actions['view_toggle_control_dock'].setChecked(self.control_dock.isVisible())
            self._menu_actions['view_toggle_bottom_log'].setChecked(self.bottom_dock.isVisible())
            self._menu_actions['view_toggle_device_explorer'].setChecked(self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['device']))
            self._menu_actions['view_toggle_signal_explorer'].setChecked(self.explorer_tabs.isTabVisible(self.explorer_tab_indexes['signal']))
            self._menu_actions['view_toggle_trace_inspector'].setChecked(self.control_tabs.isTabVisible(self.control_tab_indexes['trace']))
            self._menu_actions['view_toggle_notes'].setChecked(self.control_tabs.isTabVisible(self.control_tab_indexes['notes']))
            QtCore.QTimer.singleShot(0, self._clamp_and_commit_pip_geometry)


        def _qt_rect_to_policy_rect(self, rect: Any) -> Rect:
            return Rect(x=int(rect.x()), y=int(rect.y()), width=int(rect.width()), height=int(rect.height()))

        def _available_policy_rect(self) -> Rect:
            screen = self.screen() or QtWidgets.QApplication.primaryScreen()
            available = screen.availableGeometry()
            return self._qt_rect_to_policy_rect(available)

        def _apply_policy_rect(self, rect: Rect) -> None:
            self.setGeometry(rect.x, rect.y, rect.width, rect.height)

        def _restore_window_geometry_from_policy(self) -> None:
            available = self._available_policy_rect()
            schema_version = self.settings.value('window/layout_schema_version', 0, type=int)
            raw_geometry = self.settings.value('window/normal_geometry_json', '', type=str)
            if schema_version != self._layout_schema_version or not raw_geometry:
                self._apply_policy_rect(default_window_rect(available=available))
                return
            try:
                requested = deserialize_rect(json.loads(raw_geometry))
            except json.JSONDecodeError:
                requested = None
            if requested is None:
                self._apply_policy_rect(default_window_rect(available=available))
                return
            decision = clamp_window_rect(requested=requested, available=available)
            self._apply_policy_rect(decision.resolved)
            if self.settings.value('window/maximized', False, type=bool):
                self.showMaximized()

        def _reset_layout_cache(self) -> None:
            for key in (
                'window/layout_schema_version',
                'window/normal_geometry_json',
                'window/maximized',
                'ui/outer_splitter_sizes_json',
                'ui/center_splitter_sizes_json',
                'ui/graph_presentation',
                'ui/graph_presentation_override',
                'ui/pip_rect_json',
            ):
                self.settings.remove(key)
            self._restore_default_layout()
            self._apply_policy_rect(default_window_rect(available=self._available_policy_rect()))
            self.statusBar().showMessage('Layout cache cleared and default geometry restored', 3000)

        def _configure_autosave_timer(self) -> None:
            if hasattr(self, '_autosave_timer'):
                self._autosave_timer.stop()
            self._autosave_timer = QtCore.QTimer(self)
            self._autosave_timer.timeout.connect(self._save_settings)
            if self.autosave_enabled:
                self._autosave_timer.start(max(15, self.autosave_interval_seconds) * 1000)

        def _start_timers(self) -> None:
            self._render_timer = QtCore.QTimer(self)
            self._render_timer.timeout.connect(self._render_step)
            self._render_timer.start(120)
            self._configure_autosave_timer()

        def closeEvent(self, event: QtGui.QCloseEvent) -> None:
            self._save_settings()
            if self._diagnostics_path is not None:
                try:
                    self._write_diagnostics_payload(self._diagnostics_path)
                except Exception as exc:
                    self.statusBar().showMessage(f'Failed to write diagnostics: {exc}', 5000)
            super().closeEvent(event)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    app.setApplicationName(_GUI_SETTINGS_APP)
    app.setOrganizationName(_GUI_SETTINGS_ORG)
    window = OperatorShellWindow(
        spec=build_visible_shell_spec_for_demo(active_scenario_id=initial_scenario_id),
        diagnostics_path=diagnostics_path,
        bench_mode=bench_mode,
    )
    window.show()
    return app.exec()
