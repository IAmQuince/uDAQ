from __future__ import annotations

from dataclasses import dataclass, replace

from universaldaq.adapters import DeviceLifecyclePhase, DiscoveredDevice, WorkbenchDescriptor
from universaldaq.common import EventTime, GraphMode, RestoreOrigin
from universaldaq.profiles import WorkspaceState

from .models import (
    AuthoritySurface,
    BindingReviewSummary,
    FirstSignalSummary,
    DeviceLifecycleSummary,
    GraphModeSession,
    ReconciliationSummary,
    ActionAuditEntry,
    SessionEventSummary,
    TrustedSessionSummary,
    VariableHealthSummary,
    WorkbenchReviewState,
)
from .session_state import UISessionState


@dataclass(frozen=True, slots=True, kw_only=True)
class GraphPanelViewModel:
    mode: GraphMode
    page: str
    visible_trace_count: int
    status_label: str
    overlay_count: int = 0
    return_to_live_available: bool = False
    selected_range: tuple[EventTime, EventTime] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class DeviceCardViewModel:
    device_key: str
    display_name: str
    support_tier: str
    capability_labels: tuple[str, ...] = ()
    serial_number: str | None = None
    transport: str | None = None
    quick_start_allowed: bool = False
    advanced_setup_allowed: bool = False
    known_device: bool = False
    active: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleSummaryCardViewModel:
    phase: str
    detected_device_count: int
    active_device_key: str | None
    active_adapter_id: str | None
    projected_point_count: int
    published_signal_count: int
    last_poll_snapshot_count: int
    disconnected_signal_count: int
    last_transition: str | None
    needs_review: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class BindingReviewCardViewModel:
    total_signal_binding_count: int
    total_output_binding_count: int
    resolved_signal_count: int
    auto_rebound_signal_count: int
    manual_review_signal_count: int
    unresolved_signal_count: int
    blocked_signal_count: int
    resolved_output_count: int
    unresolved_output_count: int
    highlighted_items: tuple[str, ...]
    requires_review: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class VariableHealthCardViewModel:
    total_variable_count: int
    healthy_count: int
    substituted_count: int
    stale_count: int
    invalid_count: int
    unresolved_count: int
    degraded_count: int
    highlighted_variables: tuple[str, ...]
    impacted_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ReconciliationCardViewModel:
    outcome_kind: str | None
    confidence: str | None
    reason: str | None
    remap_candidate_count: int
    auto_rebound_signal_count: int
    manual_review_required: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkbenchCardViewModel:
    total_workbench_count: int
    available_workbench_names: tuple[str, ...]
    active_workbench_name: str | None
    highlighted_workbenches: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class FirstSignalCardViewModel:
    signal_id: str
    display_name: str
    point_key: str
    point_class: str
    latest_value: str
    quality_label: str
    latest_timestamp: EventTime | None = None
    engineering_units: str | None = None
    auto_bound: bool = False
    source_device_key: str | None = None
    source_adapter_id: str | None = None
    device_identity_key: str | None = None
    source_transport: str | None = None
    hardware_channel: str | None = None
    freshness_label: str = 'pending'
    provenance_label: str | None = None
    channel_metadata: tuple[tuple[str, str], ...] = ()
    trace_point_count: int = 0
    latest_numeric_value: float | None = None



@dataclass(frozen=True, slots=True, kw_only=True)
class ShellViewModel:
    page: str
    graph_panel: GraphPanelViewModel
    authority_label: str
    overlay_names: tuple[str, ...] = ()
    last_restore_origin: str | None = None
    restore_is_safe: bool = True
    export_preview: str | None = None
    last_export_manifest_id: str | None = None
    last_export_summary: str | None = None
    last_export_warning_count: int = 0
    actor_role_label: str | None = None
    granted_capabilities: tuple[str, ...] = ()
    last_authorization_action: str | None = None
    last_authorization_allowed: bool | None = None
    last_authorization_reason: str | None = None
    device_phase: str = DeviceLifecyclePhase.NO_DEVICE.value
    detected_devices: tuple[DeviceCardViewModel, ...] = ()
    active_device: DeviceCardViewModel | None = None
    onboarding_mode: str | None = None
    known_device_restore_offer: str | None = None
    available_workbenches: tuple[str, ...] = ()
    lifecycle_summary: LifecycleSummaryCardViewModel | None = None
    binding_review_summary: BindingReviewCardViewModel | None = None
    variable_health_summary: VariableHealthCardViewModel | None = None
    reconciliation_summary: ReconciliationCardViewModel | None = None
    workbench_review_state: WorkbenchCardViewModel | None = None
    first_signal_summary: FirstSignalCardViewModel | None = None
    trusted_session_summary: TrustedSessionSummary | None = None
    preferred_adapter_id: str | None = None
    preferred_device_key: str | None = None
    preferred_channel_key: str | None = None
    restored_historical_context_label: str | None = None
    last_session_summary_id: str | None = None
    last_session_summary_label: str | None = None
    session_note_count: int = 0
    pending_note_draft: str | None = None


class ShellViewModelBuilder:
    @staticmethod
    def _device_card(*, device, active_device_key: str | None) -> DeviceCardViewModel:
        return DeviceCardViewModel(
            device_key=device.device_key,
            display_name=device.display_name,
            support_tier=device.support_tier.value,
            capability_labels=device.capability_labels,
            serial_number=device.identity.serial_number,
            transport=device.identity.transport,
            quick_start_allowed=device.quick_start_allowed,
            advanced_setup_allowed=device.advanced_setup_allowed,
            known_device=device.known_device_key is not None,
            active=device.device_key == active_device_key,
        )

    @staticmethod
    def _lifecycle_summary(summary: DeviceLifecycleSummary | None, *, device_phase: DeviceLifecyclePhase, detected_devices: tuple[DiscoveredDevice, ...], active_device: DiscoveredDevice | None, active_adapter_id: str | None) -> LifecycleSummaryCardViewModel | None:
        if summary is None and not detected_devices and active_device is None:
            return None
        base = summary or DeviceLifecycleSummary(
            phase=device_phase.value,
            detected_device_count=len(detected_devices),
            active_device_key=None if active_device is None else active_device.device_key,
            active_adapter_id=active_adapter_id,
        )
        return LifecycleSummaryCardViewModel(
            phase=base.phase,
            detected_device_count=base.detected_device_count,
            active_device_key=base.active_device_key,
            active_adapter_id=base.active_adapter_id,
            projected_point_count=base.projected_point_count,
            published_signal_count=base.published_signal_count,
            last_poll_snapshot_count=base.last_poll_snapshot_count,
            disconnected_signal_count=base.disconnected_signal_count,
            last_transition=base.last_transition,
            needs_review=base.needs_review,
        )

    @staticmethod
    def _binding_summary(summary: BindingReviewSummary | None) -> BindingReviewCardViewModel | None:
        if summary is None:
            return None
        return BindingReviewCardViewModel(
            total_signal_binding_count=summary.total_signal_binding_count,
            total_output_binding_count=summary.total_output_binding_count,
            resolved_signal_count=summary.resolved_signal_count,
            auto_rebound_signal_count=summary.auto_rebound_signal_count,
            manual_review_signal_count=summary.manual_review_signal_count,
            unresolved_signal_count=summary.unresolved_signal_count,
            blocked_signal_count=summary.blocked_signal_count,
            resolved_output_count=summary.resolved_output_count,
            unresolved_output_count=summary.unresolved_output_count,
            highlighted_items=summary.highlighted_items,
            requires_review=summary.requires_review,
        )

    @staticmethod
    def _variable_summary(summary: VariableHealthSummary | None) -> VariableHealthCardViewModel | None:
        if summary is None:
            return None
        return VariableHealthCardViewModel(
            total_variable_count=summary.total_variable_count,
            healthy_count=summary.healthy_count,
            substituted_count=summary.substituted_count,
            stale_count=summary.stale_count,
            invalid_count=summary.invalid_count,
            unresolved_count=summary.unresolved_count,
            degraded_count=summary.degraded_count,
            highlighted_variables=summary.highlighted_variables,
            impacted_count=summary.impacted_count,
        )

    @staticmethod
    def _reconciliation_summary(summary: ReconciliationSummary | None) -> ReconciliationCardViewModel | None:
        if summary is None:
            return None
        return ReconciliationCardViewModel(
            outcome_kind=summary.outcome_kind,
            confidence=summary.confidence,
            reason=summary.reason,
            remap_candidate_count=summary.remap_candidate_count,
            auto_rebound_signal_count=summary.auto_rebound_signal_count,
            manual_review_required=summary.manual_review_required,
        )

    @staticmethod
    def _first_signal_summary(summary: FirstSignalSummary | None) -> FirstSignalCardViewModel | None:
        if summary is None:
            return None
        latest_numeric = None
        try:
            latest_numeric = float(summary.latest_value)
        except (TypeError, ValueError):
            latest_numeric = None
        return FirstSignalCardViewModel(
            signal_id=summary.signal_id,
            display_name=summary.display_name,
            point_key=summary.point_key,
            point_class=summary.point_class,
            latest_value=summary.latest_value,
            quality_label=summary.quality_label,
            latest_timestamp=summary.latest_timestamp,
            engineering_units=summary.engineering_units,
            auto_bound=summary.auto_bound,
            source_device_key=summary.source_device_key,
            source_adapter_id=summary.source_adapter_id,
            device_identity_key=summary.device_identity_key,
            source_transport=summary.source_transport,
            hardware_channel=summary.hardware_channel,
            freshness_label=summary.freshness_label,
            provenance_label=summary.provenance_label,
            channel_metadata=tuple((str(key), str(value)) for key, value in sorted(summary.channel_metadata.items())),
            trace_point_count=summary.trace_point_count,
            latest_numeric_value=latest_numeric,
        )

    @staticmethod
    def _workbench_state(summary: WorkbenchReviewState | None, *, available_workbenches: tuple[WorkbenchDescriptor, ...]) -> WorkbenchCardViewModel | None:
        if summary is None and not available_workbenches:
            return None
        base = summary or WorkbenchReviewState(
            total_workbench_count=len(available_workbenches),
            available_workbench_names=tuple(item.display_name for item in available_workbenches),
        )
        return WorkbenchCardViewModel(
            total_workbench_count=base.total_workbench_count,
            available_workbench_names=base.available_workbench_names,
            active_workbench_name=base.active_workbench_name,
            highlighted_workbenches=base.highlighted_workbenches,
        )

    @staticmethod
    def build(
        *,
        workspace_state: WorkspaceState,
        authority_surface: AuthoritySurface,
        graph_session: GraphModeSession,
        overlays: tuple[str, ...] = (),
        selected_range: tuple[EventTime, EventTime] | None = None,
        last_restore_origin: RestoreOrigin | None = None,
        restore_machine_write_intent: bool = False,
        export_scope_preview: str | None = None,
        last_export_manifest_id: str | None = None,
        last_export_summary: str | None = None,
        last_export_warning_count: int = 0,
        actor_role_label: str | None = None,
        granted_capabilities: tuple[str, ...] = (),
        last_authorization_action: str | None = None,
        last_authorization_allowed: bool | None = None,
        last_authorization_reason: str | None = None,
        device_phase: DeviceLifecyclePhase = DeviceLifecyclePhase.NO_DEVICE,
        detected_devices: tuple[DiscoveredDevice, ...] = (),
        active_device: DiscoveredDevice | None = None,
        active_adapter_id: str | None = None,
        onboarding_mode: str | None = None,
        known_device_restore_offer: str | None = None,
        available_workbenches: tuple[WorkbenchDescriptor, ...] = (),
        lifecycle_summary: DeviceLifecycleSummary | None = None,
        binding_review_summary: BindingReviewSummary | None = None,
        variable_health_summary: VariableHealthSummary | None = None,
        reconciliation_summary: ReconciliationSummary | None = None,
        workbench_review_state: WorkbenchReviewState | None = None,
        first_signal_summary: FirstSignalSummary | None = None,
    ) -> ShellViewModel:
        panel = GraphPanelViewModel(
            mode=graph_session.mode,
            page=workspace_state.page,
            visible_trace_count=len(workspace_state.visible_traces),
            status_label=authority_surface.status_label,
            overlay_count=len(overlays),
            return_to_live_available=graph_session.return_to_live_available,
            selected_range=selected_range,
        )
        active_device_key = None if active_device is None else active_device.device_key
        detected_cards = tuple(ShellViewModelBuilder._device_card(device=device, active_device_key=active_device_key) for device in detected_devices)
        active_card = None if active_device is None else ShellViewModelBuilder._device_card(device=active_device, active_device_key=active_device_key)
        workbench_names = tuple(item.display_name for item in available_workbenches)
        return ShellViewModel(
            page=workspace_state.page,
            graph_panel=panel,
            authority_label=authority_surface.status_label,
            overlay_names=overlays,
            last_restore_origin=None if last_restore_origin is None else last_restore_origin.value,
            restore_is_safe=not restore_machine_write_intent,
            export_preview=export_scope_preview,
            last_export_manifest_id=last_export_manifest_id,
            last_export_summary=last_export_summary,
            last_export_warning_count=last_export_warning_count,
            actor_role_label=actor_role_label,
            granted_capabilities=granted_capabilities,
            last_authorization_action=last_authorization_action,
            last_authorization_allowed=last_authorization_allowed,
            last_authorization_reason=last_authorization_reason,
            device_phase=device_phase.value,
            detected_devices=detected_cards,
            active_device=active_card,
            onboarding_mode=onboarding_mode,
            known_device_restore_offer=known_device_restore_offer,
            available_workbenches=workbench_names,
            lifecycle_summary=ShellViewModelBuilder._lifecycle_summary(
                lifecycle_summary,
                device_phase=device_phase,
                detected_devices=detected_devices,
                active_device=active_device,
                active_adapter_id=active_adapter_id,
            ),
            binding_review_summary=ShellViewModelBuilder._binding_summary(binding_review_summary),
            variable_health_summary=ShellViewModelBuilder._variable_summary(variable_health_summary),
            reconciliation_summary=ShellViewModelBuilder._reconciliation_summary(reconciliation_summary),
            workbench_review_state=ShellViewModelBuilder._workbench_state(workbench_review_state, available_workbenches=available_workbenches),
            first_signal_summary=ShellViewModelBuilder._first_signal_summary(first_signal_summary),
            preferred_adapter_id=None,
            preferred_device_key=None,
            preferred_channel_key=None,
            restored_historical_context_label=None,
            last_session_summary_id=None,
            last_session_summary_label=None,
            session_note_count=0,
            pending_note_draft=None,
        )

    @staticmethod
    def build_from_ui_session(ui_session: UISessionState) -> ShellViewModel:
        base = ShellViewModelBuilder.build(
            workspace_state=ui_session.workspace_state,
            authority_surface=ui_session.authority_surface,
            graph_session=ui_session.graph_session,
            overlays=ui_session.overlays,
            selected_range=ui_session.selected_range,
            last_restore_origin=ui_session.last_restore_origin,
            restore_machine_write_intent=ui_session.restore_machine_write_intent,
            export_scope_preview=ui_session.export_scope_preview,
            last_export_manifest_id=ui_session.last_export_manifest_id,
            last_export_summary=ui_session.last_export_summary,
            last_export_warning_count=ui_session.last_export_warning_count,
            actor_role_label=ui_session.actor_role_label,
            granted_capabilities=ui_session.granted_capabilities,
            last_authorization_action=ui_session.last_authorization_action,
            last_authorization_allowed=ui_session.last_authorization_allowed,
            last_authorization_reason=ui_session.last_authorization_reason,
            device_phase=ui_session.device_lifecycle_phase,
            detected_devices=ui_session.detected_devices,
            active_device=ui_session.active_device,
            active_adapter_id=ui_session.active_adapter_id,
            onboarding_mode=ui_session.onboarding_mode,
            known_device_restore_offer=ui_session.known_device_restore_offer,
            available_workbenches=ui_session.available_workbenches,
            lifecycle_summary=ui_session.lifecycle_summary,
            binding_review_summary=ui_session.binding_review_summary,
            variable_health_summary=ui_session.variable_health_summary,
            reconciliation_summary=ui_session.reconciliation_summary,
            workbench_review_state=ui_session.workbench_review_state,
            first_signal_summary=ui_session.first_signal_summary,
        )
        return replace(
            base,
            preferred_adapter_id=ui_session.preferred_adapter_id,
            preferred_device_key=ui_session.preferred_device_key,
            preferred_channel_key=ui_session.preferred_channel_key,
            restored_historical_context_label=ui_session.restored_historical_context_label,
            last_session_summary_id=ui_session.last_session_summary_id,
            last_session_summary_label=ui_session.last_session_summary_label,
            session_note_count=ui_session.session_note_count,
            pending_note_draft=ui_session.pending_note_draft,
        )
