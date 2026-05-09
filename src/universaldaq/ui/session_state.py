from __future__ import annotations

from dataclasses import dataclass, replace

from universaldaq.adapters import DeviceLifecyclePhase, DiscoveredDevice, WorkbenchDescriptor
from universaldaq.common import EventTime, ProfileId, RestoreOrigin
from universaldaq.profiles import RestoreResult, WorkspaceState
from universaldaq.security import AuthorizationDecision

from .models import (
    AuthoritySurface,
    BindingReviewSummary,
    FirstSignalSummary,
    DeviceLifecycleSummary,
    GraphModeSession,
    ReconciliationSummary,
    VariableHealthSummary,
    WorkbenchReviewState,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class UISessionState:
    workspace_state: WorkspaceState
    authority_surface: AuthoritySurface
    graph_session: GraphModeSession
    overlays: tuple[str, ...] = ()
    selected_range: tuple[EventTime, EventTime] | None = None
    last_restore_origin: RestoreOrigin | None = None
    restore_machine_write_intent: bool = False
    restore_profile_id: ProfileId | None = None
    export_scope_preview: str | None = None
    last_export_manifest_id: str | None = None
    last_export_summary: str | None = None
    last_export_warning_count: int = 0
    actor_role_label: str | None = None
    granted_capabilities: tuple[str, ...] = ()
    last_authorization_action: str | None = None
    last_authorization_allowed: bool | None = None
    last_authorization_reason: str | None = None
    device_lifecycle_phase: DeviceLifecyclePhase = DeviceLifecyclePhase.NO_DEVICE
    detected_devices: tuple[DiscoveredDevice, ...] = ()
    active_device: DiscoveredDevice | None = None
    active_adapter_id: str | None = None
    onboarding_mode: str | None = None
    known_device_restore_offer: str | None = None
    available_workbenches: tuple[WorkbenchDescriptor, ...] = ()
    lifecycle_summary: DeviceLifecycleSummary | None = None
    binding_review_summary: BindingReviewSummary | None = None
    variable_health_summary: VariableHealthSummary | None = None
    reconciliation_summary: ReconciliationSummary | None = None
    workbench_review_state: WorkbenchReviewState | None = None
    first_signal_summary: FirstSignalSummary | None = None
    preferred_adapter_id: str | None = None
    preferred_device_key: str | None = None
    preferred_channel_key: str | None = None
    restored_historical_context_label: str | None = None
    last_session_summary_id: str | None = None
    last_session_summary_label: str | None = None
    session_note_count: int = 0
    pending_note_draft: str | None = None

    @property
    def page(self) -> str:
        return self.workspace_state.page

    @property
    def visible_trace_count(self) -> int:
        return len(self.workspace_state.visible_traces)

    @property
    def return_to_live_available(self) -> bool:
        return self.graph_session.return_to_live_available

    @property
    def canonical_active_device_key(self) -> str | None:
        return None if self.active_device is None else self.active_device.device_key

    @property
    def canonical_device_identity_key(self) -> str | None:
        return None if self.active_device is None else self.active_device.identity.stable_key

    def with_workspace_state(self, workspace_state: WorkspaceState) -> 'UISessionState':
        return replace(self, workspace_state=workspace_state)

    def with_graph_session(self, graph_session: GraphModeSession) -> 'UISessionState':
        return replace(self, graph_session=graph_session)

    def with_overlays(self, overlays: tuple[str, ...]) -> 'UISessionState':
        return replace(self, overlays=overlays)

    def with_selected_range(self, selected_range: tuple[EventTime, EventTime] | None) -> 'UISessionState':
        return replace(self, selected_range=selected_range)

    def with_export_preview(self, export_scope_preview: str | None) -> 'UISessionState':
        return replace(self, export_scope_preview=export_scope_preview)

    def with_export_result(
        self,
        *,
        manifest_id: str | None,
        summary: str | None,
        warning_count: int,
    ) -> 'UISessionState':
        return replace(
            self,
            last_export_manifest_id=manifest_id,
            last_export_summary=summary,
            last_export_warning_count=warning_count,
        )

    def with_authorization_context(self, *, actor_role_label: str | None, granted_capabilities: tuple[str, ...]) -> 'UISessionState':
        return replace(self, actor_role_label=actor_role_label, granted_capabilities=granted_capabilities)

    def with_authorization_decision(self, decision: AuthorizationDecision) -> 'UISessionState':
        return replace(
            self,
            last_authorization_action=decision.action.value,
            last_authorization_allowed=decision.allowed,
            last_authorization_reason=decision.reason_text,
        )

    def with_detected_devices(self, detected_devices: tuple[DiscoveredDevice, ...], *, phase: DeviceLifecyclePhase) -> 'UISessionState':
        return replace(self, detected_devices=detected_devices, device_lifecycle_phase=phase)

    def with_lifecycle_context(
        self,
        *,
        phase: DeviceLifecyclePhase,
        detected_devices: tuple[DiscoveredDevice, ...] | None = None,
        active_device: DiscoveredDevice | None = None,
        active_adapter_id: str | None = None,
        onboarding_mode: str | None = None,
        known_device_restore_offer: str | None = None,
        available_workbenches: tuple[WorkbenchDescriptor, ...] | None = None,
    ) -> 'UISessionState':
        return replace(
            self,
            device_lifecycle_phase=phase,
            detected_devices=self.detected_devices if detected_devices is None else detected_devices,
            active_device=self.active_device if active_device is None else active_device,
            active_adapter_id=self.active_adapter_id if active_adapter_id is None else active_adapter_id,
            onboarding_mode=self.onboarding_mode if onboarding_mode is None else onboarding_mode,
            known_device_restore_offer=self.known_device_restore_offer if known_device_restore_offer is None else known_device_restore_offer,
            available_workbenches=self.available_workbenches if available_workbenches is None else available_workbenches,
        )

    def with_active_device(
        self,
        *,
        active_device: DiscoveredDevice,
        active_adapter_id: str | None,
        phase: DeviceLifecyclePhase,
        onboarding_mode: str | None,
        known_device_restore_offer: str | None,
        available_workbenches: tuple[WorkbenchDescriptor, ...],
    ) -> 'UISessionState':
        return replace(
            self,
            active_device=active_device,
            active_adapter_id=active_adapter_id,
            device_lifecycle_phase=phase,
            onboarding_mode=onboarding_mode,
            known_device_restore_offer=known_device_restore_offer,
            available_workbenches=available_workbenches,
        )

    def with_device_phase(self, *, phase: DeviceLifecyclePhase, onboarding_mode: str | None = None) -> 'UISessionState':
        return replace(self, device_lifecycle_phase=phase, onboarding_mode=onboarding_mode)

    def with_device_disconnect(self, *, phase: DeviceLifecyclePhase) -> 'UISessionState':
        return replace(self, device_lifecycle_phase=phase)

    def with_review_state(
        self,
        *,
        lifecycle_summary: DeviceLifecycleSummary | None = None,
        binding_review_summary: BindingReviewSummary | None = None,
        variable_health_summary: VariableHealthSummary | None = None,
        reconciliation_summary: ReconciliationSummary | None = None,
        workbench_review_state: WorkbenchReviewState | None = None,
        first_signal_summary: FirstSignalSummary | None = None,
    ) -> 'UISessionState':
        return replace(
            self,
            lifecycle_summary=self.lifecycle_summary if lifecycle_summary is None else lifecycle_summary,
            binding_review_summary=self.binding_review_summary if binding_review_summary is None else binding_review_summary,
            variable_health_summary=self.variable_health_summary if variable_health_summary is None else variable_health_summary,
            reconciliation_summary=self.reconciliation_summary if reconciliation_summary is None else reconciliation_summary,
            workbench_review_state=self.workbench_review_state if workbench_review_state is None else workbench_review_state,
            first_signal_summary=self.first_signal_summary if first_signal_summary is None else first_signal_summary,
        )


    def with_persistence_context(
        self,
        *,
        preferred_adapter_id: str | None = None,
        preferred_device_key: str | None = None,
        preferred_channel_key: str | None = None,
        restored_historical_context_label: str | None = None,
        last_session_summary_id: str | None = None,
        last_session_summary_label: str | None = None,
        session_note_count: int | None = None,
        pending_note_draft: str | None = None,
    ) -> 'UISessionState':
        return replace(
            self,
            preferred_adapter_id=self.preferred_adapter_id if preferred_adapter_id is None else preferred_adapter_id,
            preferred_device_key=self.preferred_device_key if preferred_device_key is None else preferred_device_key,
            preferred_channel_key=self.preferred_channel_key if preferred_channel_key is None else preferred_channel_key,
            restored_historical_context_label=self.restored_historical_context_label if restored_historical_context_label is None else restored_historical_context_label,
            last_session_summary_id=self.last_session_summary_id if last_session_summary_id is None else last_session_summary_id,
            last_session_summary_label=self.last_session_summary_label if last_session_summary_label is None else last_session_summary_label,
            session_note_count=self.session_note_count if session_note_count is None else session_note_count,
            pending_note_draft=self.pending_note_draft if pending_note_draft is None else pending_note_draft,
        )


class UISessionFactory:
    @staticmethod
    def from_restore(
        *,
        restore_result: RestoreResult,
        authority_surface: AuthoritySurface,
        graph_session: GraphModeSession,
        actor_role_label: str | None = None,
        granted_capabilities: tuple[str, ...] = (),
    ) -> UISessionState:
        return UISessionState(
            workspace_state=restore_result.restored_workspace,
            authority_surface=authority_surface,
            graph_session=graph_session,
            overlays=(),
            selected_range=None,
            last_restore_origin=restore_result.origin,
            restore_machine_write_intent=restore_result.machine_write_intent,
            restore_profile_id=restore_result.profile_id,
            actor_role_label=actor_role_label,
            granted_capabilities=granted_capabilities,
            device_lifecycle_phase=DeviceLifecyclePhase.NO_DEVICE,
        )
