from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import json
from typing import Any, Iterable, Mapping


class ExplorerTabId(StrEnum):
    DEVICE = 'device'
    SIGNAL = 'signal'
    LOGIC = 'logic'


class ControlTabId(StrEnum):
    SESSION = 'session'
    SIGNALS = 'signals'
    TRACE = 'trace'
    NOTES = 'notes'
    DIAGNOSTICS = 'diagnostics'


@dataclass(frozen=True, slots=True, kw_only=True)
class ShellPanelVisibility:
    device_explorer_visible: bool = True
    signal_explorer_visible: bool = True
    control_column_visible: bool = True
    events_console_visible: bool = True
    trace_inspector_visible: bool = True
    notes_visible: bool = True

    def to_dict(self) -> dict[str, bool]:
        return {
            'device_explorer_visible': self.device_explorer_visible,
            'signal_explorer_visible': self.signal_explorer_visible,
            'control_column_visible': self.control_column_visible,
            'events_console_visible': self.events_console_visible,
            'trace_inspector_visible': self.trace_inspector_visible,
            'notes_visible': self.notes_visible,
        }

    @staticmethod
    def from_dict(payload: Mapping[str, Any] | None) -> 'ShellPanelVisibility':
        payload = payload or {}
        return ShellPanelVisibility(
            device_explorer_visible=bool(payload.get('device_explorer_visible', True)),
            signal_explorer_visible=bool(payload.get('signal_explorer_visible', True)),
            control_column_visible=bool(payload.get('control_column_visible', True)),
            events_console_visible=bool(payload.get('events_console_visible', True)),
            trace_inspector_visible=bool(payload.get('trace_inspector_visible', True)),
            notes_visible=bool(payload.get('notes_visible', True)),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ShellLayoutSnapshot:
    workspace_id: str
    explorer_tab_id: str = ExplorerTabId.SIGNAL.value
    control_tab_id: str = ControlTabId.SESSION.value
    horizontal_sizes: tuple[int, int, int] = (300, 1040, 360)
    center_vertical_sizes: tuple[int, int] = (780, 220)
    panel_visibility: ShellPanelVisibility = field(default_factory=ShellPanelVisibility)

    def to_dict(self) -> dict[str, Any]:
        return {
            'workspace_id': self.workspace_id,
            'explorer_tab_id': self.explorer_tab_id,
            'control_tab_id': self.control_tab_id,
            'horizontal_sizes': list(self.horizontal_sizes),
            'center_vertical_sizes': list(self.center_vertical_sizes),
            'panel_visibility': self.panel_visibility.to_dict(),
        }

    @staticmethod
    def from_dict(payload: Mapping[str, Any]) -> 'ShellLayoutSnapshot':
        horizontal = tuple(int(item) for item in payload.get('horizontal_sizes', (300, 1040, 360)))
        center = tuple(int(item) for item in payload.get('center_vertical_sizes', (780, 220)))
        if len(horizontal) != 3:
            horizontal = (300, 1040, 360)
        if len(center) != 2:
            center = (780, 220)
        return ShellLayoutSnapshot(
            workspace_id=str(payload.get('workspace_id', 'operate')),
            explorer_tab_id=str(payload.get('explorer_tab_id', ExplorerTabId.SIGNAL.value)),
            control_tab_id=str(payload.get('control_tab_id', ControlTabId.SESSION.value)),
            horizontal_sizes=horizontal,
            center_vertical_sizes=center,
            panel_visibility=ShellPanelVisibility.from_dict(payload.get('panel_visibility')),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SavedShellView:
    name: str
    snapshot: ShellLayoutSnapshot
    built_in: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'built_in': self.built_in,
            'snapshot': self.snapshot.to_dict(),
        }

    @staticmethod
    def from_dict(payload: Mapping[str, Any]) -> 'SavedShellView':
        return SavedShellView(
            name=str(payload.get('name', 'Unnamed View')),
            built_in=bool(payload.get('built_in', False)),
            snapshot=ShellLayoutSnapshot.from_dict(payload.get('snapshot', {})),
        )


class ShellViewCatalog:
    def __init__(self, *, built_ins: Iterable[SavedShellView] = (), custom_views: Iterable[SavedShellView] = ()) -> None:
        self._built_ins: dict[str, SavedShellView] = {item.name: item for item in built_ins}
        self._custom_views: dict[str, SavedShellView] = {item.name: item for item in custom_views}

    @staticmethod
    def default() -> 'ShellViewCatalog':
        return ShellViewCatalog(built_ins=default_shell_views())

    @property
    def built_in_names(self) -> tuple[str, ...]:
        return tuple(self._built_ins.keys())

    @property
    def custom_names(self) -> tuple[str, ...]:
        return tuple(self._custom_views.keys())

    def names(self) -> tuple[str, ...]:
        return tuple(self._built_ins.keys()) + tuple(self._custom_views.keys())

    def get(self, name: str) -> SavedShellView | None:
        return self._custom_views.get(name) or self._built_ins.get(name)

    def save(self, *, name: str, snapshot: ShellLayoutSnapshot) -> SavedShellView:
        view = SavedShellView(name=name, snapshot=snapshot, built_in=False)
        self._custom_views[name] = view
        return view

    def delete(self, name: str) -> bool:
        if name in self._built_ins:
            return False
        return self._custom_views.pop(name, None) is not None

    def to_json(self) -> str:
        payload = {
            'custom_views': [view.to_dict() for view in self._custom_views.values()],
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    @staticmethod
    def from_json(raw: str | None) -> 'ShellViewCatalog':
        if not raw:
            return ShellViewCatalog.default()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return ShellViewCatalog.default()
        custom_rows = payload.get('custom_views', ())
        custom_views = [SavedShellView.from_dict(row) for row in custom_rows if isinstance(row, Mapping)]
        return ShellViewCatalog(built_ins=default_shell_views(), custom_views=custom_views)



def default_shell_views() -> tuple[SavedShellView, ...]:
    return (
        SavedShellView(
            name='Bench Default',
            built_in=True,
            snapshot=ShellLayoutSnapshot(
                workspace_id='operate',
                explorer_tab_id=ExplorerTabId.SIGNAL.value,
                control_tab_id=ControlTabId.SESSION.value,
                horizontal_sizes=(320, 980, 360),
                center_vertical_sizes=(760, 240),
                panel_visibility=ShellPanelVisibility(),
            ),
        ),
        SavedShellView(
            name='Trend Focus',
            built_in=True,
            snapshot=ShellLayoutSnapshot(
                workspace_id='operate',
                explorer_tab_id=ExplorerTabId.SIGNAL.value,
                control_tab_id=ControlTabId.TRACE.value,
                horizontal_sizes=(260, 1180, 260),
                center_vertical_sizes=(860, 140),
                panel_visibility=ShellPanelVisibility(events_console_visible=True),
            ),
        ),
        SavedShellView(
            name='Logic Workbench',
            built_in=True,
            snapshot=ShellLayoutSnapshot(
                workspace_id='logic_designer',
                explorer_tab_id=ExplorerTabId.SIGNAL.value,
                control_tab_id=ControlTabId.SIGNALS.value,
                horizontal_sizes=(320, 1000, 340),
                center_vertical_sizes=(860, 140),
                panel_visibility=ShellPanelVisibility(notes_visible=False),
            ),
        ),
        SavedShellView(
            name='Review + Notes',
            built_in=True,
            snapshot=ShellLayoutSnapshot(
                workspace_id='session_review',
                explorer_tab_id=ExplorerTabId.SIGNAL.value,
                control_tab_id=ControlTabId.NOTES.value,
                horizontal_sizes=(220, 1040, 420),
                center_vertical_sizes=(760, 240),
                panel_visibility=ShellPanelVisibility(trace_inspector_visible=False),
            ),
        ),
        SavedShellView(
            name='Alarm Watch',
            built_in=True,
            snapshot=ShellLayoutSnapshot(
                workspace_id='operate',
                explorer_tab_id=ExplorerTabId.DEVICE.value,
                control_tab_id=ControlTabId.DIAGNOSTICS.value,
                horizontal_sizes=(320, 920, 420),
                center_vertical_sizes=(700, 300),
                panel_visibility=ShellPanelVisibility(),
            ),
        ),
    )


class MappingDirection(StrEnum):
    DEVICE_INPUT_TO_INTERNAL_SIGNAL = 'device_input_to_internal_signal'
    INTERNAL_SIGNAL_TO_DEVICE_OUTPUT = 'internal_signal_to_device_output'


class MappingStatus(StrEnum):
    MAPPED = 'mapped'
    UNMAPPED = 'unmapped'
    INVALID = 'invalid'
    MISSING_SOURCE = 'missing_source'
    MISSING_DESTINATION = 'missing_destination'


class MappingAuthorityState(StrEnum):
    APPLIED = 'applied'
    DRAFT = 'draft'
    MODIFIED = 'modified'
    STALE = 'stale'
    CONFLICT = 'conflict'
    UNAVAILABLE = 'unavailable'


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingRow:
    row_id: str
    direction: MappingDirection
    source_endpoint: str
    internal_signal_name: str
    destination_endpoint: str
    status: MappingStatus
    capability_label: str
    units: str
    scale: float = 1.0
    offset: float = 0.0
    invert: bool = False
    enabled: bool = True
    live_capable: bool = False
    simulated: bool = False
    note: str = ''
    provenance_label: str = ''
    authority_state: str = MappingAuthorityState.DRAFT.value


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingSummary:
    total_count: int
    mapped_count: int
    output_count: int
    invalid_count: int
    unmapped_count: int


def _descriptor_label(descriptor: Any, lens: str, fallback: str) -> str:
    labels = getattr(descriptor, 'labels_by_lens', {})
    if isinstance(labels, Mapping):
        value = labels.get(lens)
        if value:
            return str(value)
    if hasattr(descriptor, 'label_for_lens'):
        try:
            return str(descriptor.label_for_lens(lens))
        except Exception:
            pass
    return fallback



def build_mapping_rows(
    *,
    signal_descriptors: Iterable[Any],
    writable_targets: Iterable[Any] = (),
    runtime_mode: str,
) -> tuple[MappingRow, ...]:
    rows: list[MappingRow] = []
    seen_output_endpoints: set[str] = set()
    for descriptor in signal_descriptors:
        signal_id = str(getattr(descriptor, 'signal_id', 'unknown_signal'))
        hardware_name = _descriptor_label(descriptor, 'hardware', signal_id)
        logical_name = _descriptor_label(descriptor, 'logical', signal_id)
        units = str(getattr(descriptor, 'units', ''))
        point_class = str(getattr(descriptor, 'point_class', ''))
        write_safe = bool(getattr(descriptor, 'write_safe', False))
        is_output = write_safe or point_class == 'command'
        point_id = str(getattr(descriptor, 'point_id', hardware_name))
        provenance = f'{hardware_name} ↔ {logical_name}'
        if is_output:
            destination_endpoint = hardware_name
            seen_output_endpoints.add(point_id)
            rows.append(
                MappingRow(
                    row_id=signal_id,
                    direction=MappingDirection.INTERNAL_SIGNAL_TO_DEVICE_OUTPUT,
                    source_endpoint=logical_name,
                    internal_signal_name=logical_name,
                    destination_endpoint=destination_endpoint,
                    status=MappingStatus.MAPPED if destination_endpoint else MappingStatus.MISSING_DESTINATION,
                    capability_label='writable, live-capable' if runtime_mode == 'LIVE' else 'writable, simulated',
                    units=units,
                    live_capable=runtime_mode == 'LIVE',
                    simulated=runtime_mode != 'LIVE',
                    note='Output binding path',
                    provenance_label=provenance,
                )
            )
        else:
            rows.append(
                MappingRow(
                    row_id=signal_id,
                    direction=MappingDirection.DEVICE_INPUT_TO_INTERNAL_SIGNAL,
                    source_endpoint=hardware_name,
                    internal_signal_name=logical_name,
                    destination_endpoint='',
                    status=MappingStatus.MAPPED if hardware_name and logical_name else MappingStatus.INVALID,
                    capability_label='readable, live-capable' if runtime_mode == 'LIVE' else 'readable, simulated',
                    units=units,
                    live_capable=runtime_mode == 'LIVE',
                    simulated=runtime_mode != 'LIVE',
                    note='Input binding path',
                    provenance_label=provenance,
                )
            )
    for target in writable_targets:
        point_id = str(getattr(target, 'point_id', 'unknown_output'))
        if point_id in seen_output_endpoints:
            continue
        display_name = str(getattr(target, 'display_name', point_id))
        units = str(getattr(target, 'units', ''))
        rows.append(
            MappingRow(
                row_id=f'unmapped::{point_id}',
                direction=MappingDirection.INTERNAL_SIGNAL_TO_DEVICE_OUTPUT,
                source_endpoint='',
                internal_signal_name='',
                destination_endpoint=display_name,
                status=MappingStatus.UNMAPPED,
                capability_label=str(getattr(target, 'target_class', 'writable')),
                units=units,
                live_capable=True,
                simulated=runtime_mode != 'LIVE',
                note='Available writable endpoint awaiting signal binding',
                provenance_label=display_name,
            )
        )
    return tuple(rows)



def summarize_mapping_rows(rows: Iterable[MappingRow]) -> MappingSummary:
    row_list = list(rows)
    return MappingSummary(
        total_count=len(row_list),
        mapped_count=sum(1 for item in row_list if item.status == MappingStatus.MAPPED),
        output_count=sum(1 for item in row_list if item.direction == MappingDirection.INTERNAL_SIGNAL_TO_DEVICE_OUTPUT),
        invalid_count=sum(1 for item in row_list if item.status in {MappingStatus.INVALID, MappingStatus.MISSING_DESTINATION, MappingStatus.MISSING_SOURCE}),
        unmapped_count=sum(1 for item in row_list if item.status == MappingStatus.UNMAPPED),
    )



class MappingApplyWorkflowState(StrEnum):
    READY_FOR_PREFLIGHT = 'ready_for_preflight'
    PREFLIGHT_PASSED = 'preflight_passed'
    PREFLIGHT_WARNINGS = 'preflight_warnings'
    PREFLIGHT_BLOCKED = 'preflight_blocked'
    PREPARED_REQUEST_NOT_EXECUTED = 'prepared_request_not_executed'
    CONTROLLER_DRY_RUN_ACCEPTED = 'controller_dry_run_accepted'
    CONTROLLER_DRY_RUN_REJECTED = 'controller_dry_run_rejected'


@dataclass(frozen=True, slots=True, kw_only=True)
class MappingApplyReviewPanel:
    state: MappingApplyWorkflowState
    review_text: str
    can_prepare_request: bool
    prepared_request_id: str | None = None
    executed: bool = False
    warning_count: int = 0
    blocking_count: int = 0
    dry_run_result_id: str | None = None
    dry_run_would_change_count: int = 0
    dry_run_blocked_reason: str = ''


def build_mapping_apply_review_panel(
    *,
    preflight_state: str | None,
    review_text: str,
    warning_count: int = 0,
    blocking_count: int = 0,
    prepared_request_id: str | None = None,
    executed: bool = False,
    dry_run_result_state: str | None = None,
    dry_run_result_id: str | None = None,
    dry_run_would_change_count: int = 0,
    dry_run_blocked_reason: str = '',
) -> MappingApplyReviewPanel:
    normalized_dry_run = (dry_run_result_state or '').lower()
    if normalized_dry_run:
        accepted = normalized_dry_run == 'accepted'
        status_text = (
            f'{review_text}\nController dry-run accepted; would change {dry_run_would_change_count} mapping(s); not executed live.'
            if accepted
            else f'{review_text}\nController dry-run rejected: {dry_run_blocked_reason or normalized_dry_run}; not executed live.'
        )
        return MappingApplyReviewPanel(
            state=MappingApplyWorkflowState.CONTROLLER_DRY_RUN_ACCEPTED if accepted else MappingApplyWorkflowState.CONTROLLER_DRY_RUN_REJECTED,
            review_text=status_text,
            can_prepare_request=False,
            prepared_request_id=prepared_request_id,
            executed=False,
            warning_count=warning_count,
            blocking_count=blocking_count,
            dry_run_result_id=dry_run_result_id,
            dry_run_would_change_count=dry_run_would_change_count,
            dry_run_blocked_reason=dry_run_blocked_reason,
        )
    if prepared_request_id is not None:
        return MappingApplyReviewPanel(
            state=MappingApplyWorkflowState.PREPARED_REQUEST_NOT_EXECUTED,
            review_text=f'{review_text}\nRequest {prepared_request_id} prepared only; not executed.',
            can_prepare_request=False,
            prepared_request_id=prepared_request_id,
            executed=executed,
            warning_count=warning_count,
            blocking_count=blocking_count,
        )
    normalized = (preflight_state or '').lower()
    if normalized == 'pass':
        state = MappingApplyWorkflowState.PREFLIGHT_PASSED
        can_prepare = True
    elif normalized == 'pass_with_warnings':
        state = MappingApplyWorkflowState.PREFLIGHT_WARNINGS
        can_prepare = True
    elif normalized:
        state = MappingApplyWorkflowState.PREFLIGHT_BLOCKED
        can_prepare = False
    else:
        state = MappingApplyWorkflowState.READY_FOR_PREFLIGHT
        can_prepare = False
    return MappingApplyReviewPanel(
        state=state,
        review_text=review_text,
        can_prepare_request=can_prepare,
        warning_count=warning_count,
        blocking_count=blocking_count,
        executed=executed,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class DeviceIoRow:
    row_id: str
    device_context_key: str
    signal_id: str
    endpoint_label: str
    internal_signal_name: str
    tag_name: str
    direction: str
    source_class: str
    capability_label: str
    authority_state: str
    units: str
    health_label: str = ''
    provenance_label: str = ''
    note: str = ''


@dataclass(frozen=True, slots=True, kw_only=True)
class DeviceIoSummary:
    total_count: int
    input_count: int
    output_count: int
    applied_count: int
    draft_count: int
    unavailable_count: int
    modified_count: int = 0
    stale_count: int = 0
    conflict_count: int = 0


def _authority_value(row: Mapping[str, Any] | Any | None, key: str, default: str = '') -> str:
    if row is None:
        return default
    if isinstance(row, Mapping):
        return str(row.get(key, default) or default)
    return str(getattr(row, key, default) or default)


def _endpoints_match(*, mapping_row: MappingRow | None, authority_row: Mapping[str, Any] | Any | None) -> bool:
    if mapping_row is None or authority_row is None:
        return False
    direction = _authority_value(authority_row, 'direction')
    if direction == MappingDirection.INTERNAL_SIGNAL_TO_DEVICE_OUTPUT.value:
        return mapping_row.destination_endpoint == _authority_value(authority_row, 'destination_endpoint')
    return mapping_row.source_endpoint == _authority_value(authority_row, 'source_endpoint')


def classify_mapping_authority_state(
    *,
    mapping_row: MappingRow | None,
    authority_row: Mapping[str, Any] | Any | None,
) -> MappingAuthorityState:
    if authority_row is not None:
        authority_status = _authority_value(authority_row, 'status', MappingAuthorityState.APPLIED.value).lower()
        if authority_status in {
            MappingAuthorityState.STALE.value,
            MappingAuthorityState.CONFLICT.value,
            MappingAuthorityState.UNAVAILABLE.value,
        }:
            return MappingAuthorityState(authority_status)
        if mapping_row is not None and mapping_row.status == MappingStatus.MAPPED and not _endpoints_match(
            mapping_row=mapping_row,
            authority_row=authority_row,
        ):
            return MappingAuthorityState.MODIFIED
        return MappingAuthorityState.APPLIED
    if mapping_row is not None and mapping_row.status == MappingStatus.MAPPED:
        return MappingAuthorityState.DRAFT
    return MappingAuthorityState.UNAVAILABLE


def build_device_io_rows(
    *,
    device_context_key: str,
    signal_descriptors: Iterable[Any],
    mapping_rows: Iterable[MappingRow],
    authoritative_rows: Iterable[Mapping[str, Any]] = (),
    tag_names_by_signal: Mapping[str, str] | None = None,
    runtime_mode: str,
    health_label: str = '',
) -> tuple[DeviceIoRow, ...]:
    tag_names_by_signal = {} if tag_names_by_signal is None else dict(tag_names_by_signal)
    mapping_by_signal: dict[str, MappingRow] = {}
    output_unmapped_labels: set[str] = set()
    for row in mapping_rows:
        if row.row_id.startswith('unmapped::'):
            output_unmapped_labels.add(row.destination_endpoint)
            continue
        mapping_by_signal[row.row_id] = row
    authority_by_logical: dict[str, Mapping[str, Any]] = {}
    for row in authoritative_rows:
        logical_id = _authority_value(row, 'logical_id')
        if logical_id:
            authority_by_logical[logical_id] = row
    rows: list[DeviceIoRow] = []
    for descriptor in signal_descriptors:
        signal_id = str(getattr(descriptor, 'signal_id', 'unknown_signal'))
        endpoint_label = _descriptor_label(descriptor, 'hardware', signal_id)
        internal_signal_name = _descriptor_label(descriptor, 'logical', signal_id)
        tag_name = str(tag_names_by_signal.get(signal_id) or internal_signal_name)
        mapping_row = mapping_by_signal.get(signal_id)
        authority_row = authority_by_logical.get(signal_id)
        point_class = str(getattr(descriptor, 'point_class', ''))
        write_safe = bool(getattr(descriptor, 'write_safe', False))
        direction = 'output' if write_safe or point_class == 'command' else 'input'
        source_class = 'real_output' if direction == 'output' else 'real_input'
        capability_label = 'writable' if direction == 'output' else 'readable'
        if runtime_mode == 'LIVE':
            capability_label += ', live-capable'
        else:
            capability_label += ', simulated'
        authority_state = classify_mapping_authority_state(mapping_row=mapping_row, authority_row=authority_row).value
        note_parts = [f'authority_state={authority_state}']
        if mapping_row is not None and mapping_row.note:
            note_parts.append(str(mapping_row.note))
        authority_note = _authority_value(authority_row, 'note')
        if authority_note:
            note_parts.append(authority_note)
        if direction == 'output' and endpoint_label in output_unmapped_labels:
            note_parts.append('output endpoint also advertised as available for new bindings')
        rows.append(
            DeviceIoRow(
                row_id=signal_id,
                device_context_key=device_context_key,
                signal_id=signal_id,
                endpoint_label=endpoint_label,
                internal_signal_name=internal_signal_name,
                tag_name=tag_name,
                direction=direction,
                source_class=source_class,
                capability_label=capability_label,
                authority_state=authority_state,
                units=str(getattr(descriptor, 'units', '') or ''),
                health_label=health_label or ('live' if runtime_mode == 'LIVE' else 'simulated'),
                provenance_label=str(getattr(descriptor, 'source_class', '') or source_class),
                note=' | '.join(part for part in note_parts if part),
            )
        )
    rows.sort(key=lambda item: (item.direction != 'input', item.endpoint_label.lower(), item.signal_id.lower()))
    return tuple(rows)


def summarize_device_io_rows(rows: Iterable[DeviceIoRow]) -> DeviceIoSummary:
    row_list = list(rows)
    return DeviceIoSummary(
        total_count=len(row_list),
        input_count=sum(1 for item in row_list if item.direction == 'input'),
        output_count=sum(1 for item in row_list if item.direction == 'output'),
        applied_count=sum(1 for item in row_list if item.authority_state == MappingAuthorityState.APPLIED.value),
        draft_count=sum(1 for item in row_list if item.authority_state == MappingAuthorityState.DRAFT.value),
        unavailable_count=sum(1 for item in row_list if item.authority_state == MappingAuthorityState.UNAVAILABLE.value),
        modified_count=sum(1 for item in row_list if item.authority_state == MappingAuthorityState.MODIFIED.value),
        stale_count=sum(1 for item in row_list if item.authority_state == MappingAuthorityState.STALE.value),
        conflict_count=sum(1 for item in row_list if item.authority_state == MappingAuthorityState.CONFLICT.value),
    )


def collapse_event_console_rows(rows: Iterable[EventConsoleRow]) -> tuple[EventConsoleRow, ...]:
    collapsed: list[EventConsoleRow] = []
    current: EventConsoleRow | None = None
    count = 0
    for row in rows:
        if current is None:
            current = row
            count = 1
            continue
        if (row.severity, row.category, row.message) == (current.severity, current.category, current.message):
            count += 1
            current = EventConsoleRow(
                timestamp_label=row.timestamp_label,
                severity=current.severity,
                category=current.category,
                message=current.message,
            )
            continue
        message = current.message if count == 1 else f'{current.message} (x{count})'
        collapsed.append(EventConsoleRow(timestamp_label=current.timestamp_label, severity=current.severity, category=current.category, message=message))
        current = row
        count = 1
    if current is not None:
        message = current.message if count == 1 else f'{current.message} (x{count})'
        collapsed.append(EventConsoleRow(timestamp_label=current.timestamp_label, severity=current.severity, category=current.category, message=message))
    return tuple(collapsed)


@dataclass(frozen=True, slots=True, kw_only=True)
class EventConsoleRow:
    timestamp_label: str
    severity: str
    category: str
    message: str


def derive_event_console_rows(event_log: Iterable[str], *, elapsed_seconds: float | None = None) -> tuple[EventConsoleRow, ...]:
    rows: list[EventConsoleRow] = []
    time_label = f't+{elapsed_seconds:0.1f}s' if elapsed_seconds is not None else 't+--'
    for item in event_log:
        lowered = str(item).lower()
        if any(token in lowered for token in ('critical', 'esd', 'safe state', 'blocked')):
            severity = 'critical'
        elif 'high' in lowered or 'failed' in lowered:
            severity = 'high'
        elif 'warning' in lowered or 'loaded' in lowered:
            severity = 'warning'
        else:
            severity = 'info'
        if any(token in lowered for token in ('connect', 'disconnect', 'driver', 'inventory')):
            category = 'Diagnostics'
        elif any(token in lowered for token in ('write', 'control', 'armed')):
            category = 'Actions'
        elif any(token in lowered for token in ('alarm', 'critical', 'warning', 'high')):
            category = 'Alarms'
        else:
            category = 'Runtime'
        rows.append(EventConsoleRow(timestamp_label=time_label, severity=severity, category=category, message=str(item)))
    return collapse_event_console_rows(tuple(rows))
