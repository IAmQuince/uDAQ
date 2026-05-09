from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any

from universaldaq.adapters import AdapterPollResult, DeviceLifecyclePhase, DiscoveredDevice, PointClass, ReconciliationOutcome, WorkbenchDescriptor
from universaldaq.common import EventTime, SignalId, SignalQuality, VariableId
from universaldaq.signals import (
    BindingPolicy,
    BindingReviewSummary as ServiceBindingReviewSummary,
    DevicePointDefinition,
    LogicalSignalBinding,
    SignalDefinition,
    SignalSnapshot,
    VariableDefinition,
    VariableEvaluationResult,
    VariableState,
)
from universaldaq.ui import (
    BindingReviewSummary,
    DeviceLifecycleSummary,
    ReconciliationSummary,
    VariableHealthSummary,
    WorkbenchReviewState,
)
from universaldaq.ui.session_state import UISessionState

from .service_registry import ShellServiceRegistry


@dataclass(frozen=True, slots=True, kw_only=True)
class DiscoveryWorkflowResult:
    devices: tuple[DiscoveredDevice, ...]
    lifecycle_summary: DeviceLifecycleSummary


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivationWorkflowResult:
    device: DiscoveredDevice
    adapter_id: str | None
    workbenches: tuple[WorkbenchDescriptor, ...]
    known_device_restore_offer: str | None
    lifecycle_phase: DeviceLifecyclePhase
    lifecycle_summary: DeviceLifecycleSummary
    binding_review_summary: BindingReviewSummary
    variable_health_summary: VariableHealthSummary
    reconciliation_summary: ReconciliationSummary
    workbench_review_state: WorkbenchReviewState


@dataclass(frozen=True, slots=True, kw_only=True)
class PollWorkflowResult:
    poll_results: tuple[AdapterPollResult, ...]
    lifecycle_summary: DeviceLifecycleSummary
    binding_review_summary: BindingReviewSummary
    variable_health_summary: VariableHealthSummary
    reconciliation_summary: ReconciliationSummary | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewBundle:
    lifecycle_summary: DeviceLifecycleSummary
    binding_review_summary: BindingReviewSummary
    variable_health_summary: VariableHealthSummary
    reconciliation_summary: ReconciliationSummary | None
    workbench_review_state: WorkbenchReviewState | None
    active_device_key: str | None
    active_adapter_id: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            'active_device_key': self.active_device_key,
            'active_adapter_id': self.active_adapter_id,
            'lifecycle_summary': {
                'phase': self.lifecycle_summary.phase,
                'detected_device_count': self.lifecycle_summary.detected_device_count,
                'projected_point_count': self.lifecycle_summary.projected_point_count,
                'published_signal_count': self.lifecycle_summary.published_signal_count,
                'last_poll_snapshot_count': self.lifecycle_summary.last_poll_snapshot_count,
                'disconnected_signal_count': self.lifecycle_summary.disconnected_signal_count,
                'last_transition': self.lifecycle_summary.last_transition,
                'needs_review': self.lifecycle_summary.needs_review,
            },
            'binding_review_summary': {
                'total_signal_binding_count': self.binding_review_summary.total_signal_binding_count,
                'total_output_binding_count': self.binding_review_summary.total_output_binding_count,
                'resolved_signal_count': self.binding_review_summary.resolved_signal_count,
                'auto_rebound_signal_count': self.binding_review_summary.auto_rebound_signal_count,
                'manual_review_signal_count': self.binding_review_summary.manual_review_signal_count,
                'unresolved_signal_count': self.binding_review_summary.unresolved_signal_count,
                'blocked_signal_count': self.binding_review_summary.blocked_signal_count,
                'resolved_output_count': self.binding_review_summary.resolved_output_count,
                'unresolved_output_count': self.binding_review_summary.unresolved_output_count,
                'highlighted_items': list(self.binding_review_summary.highlighted_items),
            },
            'variable_health_summary': {
                'total_variable_count': self.variable_health_summary.total_variable_count,
                'healthy_count': self.variable_health_summary.healthy_count,
                'substituted_count': self.variable_health_summary.substituted_count,
                'stale_count': self.variable_health_summary.stale_count,
                'invalid_count': self.variable_health_summary.invalid_count,
                'unresolved_count': self.variable_health_summary.unresolved_count,
                'degraded_count': self.variable_health_summary.degraded_count,
                'highlighted_variables': list(self.variable_health_summary.highlighted_variables),
            },
            'reconciliation_summary': None if self.reconciliation_summary is None else {
                'outcome_kind': self.reconciliation_summary.outcome_kind,
                'confidence': self.reconciliation_summary.confidence,
                'reason': self.reconciliation_summary.reason,
                'remap_candidate_count': self.reconciliation_summary.remap_candidate_count,
                'auto_rebound_signal_count': self.reconciliation_summary.auto_rebound_signal_count,
                'manual_review_required': self.reconciliation_summary.manual_review_required,
            },
            'workbench_review_state': None if self.workbench_review_state is None else {
                'total_workbench_count': self.workbench_review_state.total_workbench_count,
                'available_workbench_names': list(self.workbench_review_state.available_workbench_names),
                'active_workbench_name': self.workbench_review_state.active_workbench_name,
                'highlighted_workbenches': list(self.workbench_review_state.highlighted_workbenches),
            },
        }


class ShellLifecycleOrchestrator:
    def __init__(self, services: ShellServiceRegistry) -> None:
        self.services = services

    @staticmethod
    def _role_for_point(*, point_class: PointClass, readable: bool, writable: bool) -> str:
        if readable and writable:
            return f'{point_class.value}_rw'
        if writable:
            return f'{point_class.value}_output'
        if readable:
            return f'{point_class.value}_input'
        return point_class.value

    @staticmethod
    def _highlighted_binding_items(summary: ServiceBindingReviewSummary) -> tuple[str, ...]:
        highlights: list[str] = []
        for item in summary.items:
            if item.status.value in {'manual_review_required', 'unresolved', 'blocked_by_policy', 'auto_rebound'}:
                label = f'{item.binding_kind}:{item.logical_id}:{item.status.value}'
                if item.resolved_point_key is not None:
                    label = f'{label}->{item.resolved_point_key}'
                highlights.append(label)
        return tuple(highlights[:8])

    @staticmethod
    def _binding_surface(summary: ServiceBindingReviewSummary) -> BindingReviewSummary:
        return BindingReviewSummary(
            total_signal_binding_count=summary.total_signal_binding_count,
            total_output_binding_count=summary.total_output_binding_count,
            resolved_signal_count=summary.resolved_signal_count,
            auto_rebound_signal_count=summary.auto_rebound_signal_count,
            manual_review_signal_count=summary.manual_review_signal_count,
            unresolved_signal_count=summary.unresolved_signal_count,
            blocked_signal_count=summary.blocked_signal_count,
            resolved_output_count=summary.resolved_output_count,
            unresolved_output_count=summary.unresolved_output_count,
            highlighted_items=ShellLifecycleOrchestrator._highlighted_binding_items(summary),
        )

    @staticmethod
    def _workbench_surface(*, workbenches: tuple[WorkbenchDescriptor, ...]) -> WorkbenchReviewState:
        names = tuple(item.display_name for item in workbenches)
        return WorkbenchReviewState(
            total_workbench_count=len(names),
            available_workbench_names=names,
            active_workbench_name=None if not names else names[0],
            highlighted_workbenches=names[:3],
        )

    @staticmethod
    def _reconciliation_surface(
        *,
        outcome: ReconciliationOutcome | None,
        binding_summary: ServiceBindingReviewSummary,
    ) -> ReconciliationSummary:
        if outcome is None:
            return ReconciliationSummary(
                outcome_kind=None,
                confidence=None,
                reason=None,
                remap_candidate_count=0,
                auto_rebound_signal_count=binding_summary.auto_rebound_signal_count,
                manual_review_required=binding_summary.requires_review,
            )
        return ReconciliationSummary(
            outcome_kind=outcome.kind.value,
            confidence=outcome.confidence.value,
            reason=outcome.reason,
            remap_candidate_count=len(outcome.remap_candidates),
            auto_rebound_signal_count=binding_summary.auto_rebound_signal_count,
            manual_review_required=binding_summary.requires_review or len(outcome.remap_candidates) > 0,
        )

    def _evaluate_variable_health(
        self,
        *,
        timestamp: EventTime,
        changed_signal_ids: tuple[SignalId, ...] = (),
        changed_variable_ids: tuple[VariableId, ...] = (),
    ) -> VariableHealthSummary:
        previous_snapshots = dict(self.services.variables.snapshots)
        if changed_signal_ids or changed_variable_ids:
            results = self.services.variables.evaluate_impacted(
                signal_registry=self.services.signals,
                timestamp=timestamp,
                changed_signal_ids=changed_signal_ids,
                changed_variable_ids=changed_variable_ids,
            )
        else:
            results = self.services.variables.evaluate_all(signal_registry=self.services.signals, timestamp=timestamp)
        variable_stats = self.services.runtime_quality.record_variable_results(
            timestamp=timestamp,
            results=results,
            previous_snapshots=previous_snapshots,
        )
        event_result = self.services.events.evaluate_variable_snapshots(
            timestamp=timestamp,
            snapshots=self.services.variables.snapshots,
        )
        for event in event_result.events:
            self.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='event',
                payload=event.as_dict(),
            )
        changed_lifecycles = {alarm_id: self.services.events.lifecycles[alarm_id] for alarm_id in event_result.changed_alarm_ids if alarm_id in self.services.events.lifecycles}
        for alarm_id, lifecycle in changed_lifecycles.items():
            transition = lifecycle.transitions[-1] if lifecycle.transitions else None
            if transition is None:
                continue
            self.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='alarm_transition',
                payload={
                    'alarm_id': str(alarm_id),
                    'state': transition.state.value,
                    'timestamp': int(transition.timestamp),
                    'actor': None if transition.actor is None else str(transition.actor),
                },
            )
        if self.services.runtime_metrics is not None:
            self.services.runtime_metrics.set_gauge('lifecycle.changed_signal_ids.count', len(changed_signal_ids))
            self.services.runtime_metrics.set_gauge('lifecycle.requested_changed_variable_ids.count', len(changed_variable_ids))
            self.services.runtime_metrics.set_gauge('runtime.variables.requested_change_count', len(changed_variable_ids))
            self.services.runtime_metrics.set_gauge('runtime.variables.value_changed_count', variable_stats.changed_count)
            self.services.runtime_metrics.set_gauge('runtime.variables.state_changed_count', variable_stats.transition_count)
            self.services.runtime_metrics.set_gauge('variables.skipped.count', variable_stats.skipped_count)
            summary = self.services.events.summary()
            self.services.runtime_metrics.set_gauge('events.active_alarm_count', summary['active_alarm_count'])
            self.services.runtime_metrics.set_gauge('events.unacknowledged_alarm_count', summary['unacknowledged_alarm_count'])
            self.services.runtime_metrics.set_gauge('events.recent_domain_event_count', summary['recent_domain_event_count'])
        return self._variable_surface()

    def _variable_surface(self) -> VariableHealthSummary:
        snapshots = tuple(self.services.variables.snapshots.values())
        highlighted: list[str] = []
        healthy = substituted = stale = invalid = unresolved = degraded = 0
        for snapshot in snapshots:
            state = snapshot.state
            if state == VariableState.HEALTHY:
                healthy += 1
            elif state == VariableState.SUBSTITUTED:
                substituted += 1
                highlighted.append(f'{snapshot.variable_id}:substituted')
            elif state == VariableState.STALE:
                stale += 1
                highlighted.append(f'{snapshot.variable_id}:stale')
            elif state == VariableState.INVALID:
                invalid += 1
                highlighted.append(f'{snapshot.variable_id}:invalid')
            elif state == VariableState.UNRESOLVED:
                unresolved += 1
                highlighted.append(f'{snapshot.variable_id}:unresolved')
            elif state == VariableState.DEGRADED:
                degraded += 1
                highlighted.append(f'{snapshot.variable_id}:degraded')
        return VariableHealthSummary(
            total_variable_count=len(self.services.variables.definitions),
            healthy_count=healthy,
            substituted_count=substituted,
            stale_count=stale,
            invalid_count=invalid,
            unresolved_count=unresolved,
            degraded_count=degraded,
            highlighted_variables=tuple(highlighted[:8]),
        )

    @staticmethod
    def _lifecycle_surface(
        *,
        phase: DeviceLifecyclePhase,
        detected_device_count: int,
        active_device_key: str | None,
        active_adapter_id: str | None,
        projected_point_count: int,
        published_signal_count: int,
        last_poll_snapshot_count: int,
        disconnected_signal_count: int,
        last_transition: str,
        needs_review: bool,
    ) -> DeviceLifecycleSummary:
        return DeviceLifecycleSummary(
            phase=phase.value,
            detected_device_count=detected_device_count,
            active_device_key=active_device_key,
            active_adapter_id=active_adapter_id,
            projected_point_count=projected_point_count,
            published_signal_count=published_signal_count,
            last_poll_snapshot_count=last_poll_snapshot_count,
            disconnected_signal_count=disconnected_signal_count,
            last_transition=last_transition,
            needs_review=needs_review,
        )

    def discover_devices(self, *, timestamp: EventTime) -> DiscoveryWorkflowResult:
        devices = self.services.adapters.discover_devices(timestamp=timestamp)
        phase = DeviceLifecyclePhase.NO_DEVICE if not devices else DeviceLifecyclePhase.DISCOVERED
        lifecycle = self._lifecycle_surface(
            phase=phase,
            detected_device_count=len(devices),
            active_device_key=None,
            active_adapter_id=None,
            projected_point_count=0,
            published_signal_count=0,
            last_poll_snapshot_count=0,
            disconnected_signal_count=0,
            last_transition='discover_devices',
            needs_review=False,
        )
        return DiscoveryWorkflowResult(devices=devices, lifecycle_summary=lifecycle)

    def _project_point_definitions(self, *, device: DiscoveredDevice, adapter_id: str | None) -> tuple[DevicePointDefinition, ...]:
        if adapter_id is None:
            self.services.bindings.replace_device_point_definitions(device_identity_key=device.identity.stable_key, definitions=())
            return ()
        adapter = self.services.adapters.adapters.get(adapter_id)
        if adapter is None:
            self.services.bindings.replace_device_point_definitions(device_identity_key=device.identity.stable_key, definitions=())
            return ()
        capability = adapter.capability()
        writable_ids = {point.point_id for point in capability.writable_points}
        readable_ids = {point.point_id for point in capability.readable_points}
        definitions: list[DevicePointDefinition] = []
        for point in capability.readable_points + capability.writable_points:
            if any(existing.stable_point_key == point.stable_key for existing in definitions):
                continue
            definitions.append(
                DevicePointDefinition(
                    point_ref=point,
                    device_identity_key=device.identity.stable_key,
                    friendly_name=point.display_name or point.point_id,
                    role=self._role_for_point(
                        point_class=point.point_class,
                        readable=point.point_id in readable_ids,
                        writable=point.point_id in writable_ids,
                    ),
                    enabled=True,
                    metadata={
                        'device_key': device.device_key,
                        'support_tier': device.support_tier.value,
                        'provider_id': device.provider_id,
                        'point_class': point.point_class.value,
                        'units': '' if point.units is None else point.units,
                        **{str(key): str(value) for key, value in point.metadata.items()},
                    },
                )
            )
        new_definitions = tuple(definitions)
        previous_signature = self.services.bindings.point_definition_signatures.get(device.identity.stable_key)
        projected = self.services.bindings.replace_device_point_definitions(
            device_identity_key=device.identity.stable_key,
            definitions=new_definitions,
        )
        if self.services.runtime_metrics is not None:
            current_signature = self.services.bindings.point_definition_signatures.get(device.identity.stable_key)
            self.services.runtime_metrics.set_gauge('lifecycle.projected_points.count', len(projected))
            self.services.runtime_metrics.set_gauge(
                'lifecycle.projected_points.last_replace_skipped',
                int(previous_signature is not None and previous_signature == current_signature),
            )
        return projected

    def activate_detected_device(
        self,
        *,
        device_key: str,
        timestamp: EventTime,
        current_profile_id: str | None,
    ) -> ActivationWorkflowResult:
        device, adapter_id, workbenches = self.services.adapters.activate_discovered_device(device_key=device_key)
        known_offer = None
        if device.known_device_key is not None:
            known = self.services.adapters.known_devices.get(device.identity.stable_key)
            if known is not None:
                if known.last_profile_id:
                    known_offer = f'restore available from profile {known.last_profile_id}'
                else:
                    known_offer = 'recognized device; prior workspace association available'
        reconciliation = self.services.device_registry.register_or_attach(
            identity=device.identity,
            provider_id=device.provider_id,
            transport_path=device.identity.transport,
            timestamp=timestamp,
        )
        projected = self._project_point_definitions(device=device, adapter_id=adapter_id)
        binding_summary = self.services.bindings.build_binding_review(device_identity_key=device.identity.stable_key, auto_apply_rebind=True)
        phase = self.services.adapters.lifecycle_phase_for_device(device=device, active_adapter_id=adapter_id)
        lifecycle = self._lifecycle_surface(
            phase=phase,
            detected_device_count=len(self.services.adapters.discovered_devices),
            active_device_key=device.device_key,
            active_adapter_id=adapter_id,
            projected_point_count=len(projected),
            published_signal_count=binding_summary.resolved_signal_count,
            last_poll_snapshot_count=0,
            disconnected_signal_count=0,
            last_transition='activate_detected_device',
            needs_review=binding_summary.requires_review,
        )
        return ActivationWorkflowResult(
            device=device,
            adapter_id=adapter_id,
            workbenches=workbenches,
            known_device_restore_offer=known_offer,
            lifecycle_phase=phase,
            lifecycle_summary=lifecycle,
            binding_review_summary=self._binding_surface(binding_summary),
            variable_health_summary=self._variable_surface(),
            reconciliation_summary=self._reconciliation_surface(outcome=reconciliation, binding_summary=binding_summary),
            workbench_review_state=self._workbench_surface(workbenches=workbenches),
        )

    def bind_logical_signal(
        self,
        *,
        logical_signal_id: SignalId,
        point_key: str,
        display_name: str | None = None,
        binding_policy: BindingPolicy = BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
    ) -> BindingReviewSummary:
        point_definition = self.services.bindings.point_definitions[point_key]
        if logical_signal_id not in self.services.signals.definitions:
            self.services.signals.register_signal(
                SignalDefinition(
                    signal_id=logical_signal_id,
                    display_name=point_definition.friendly_name if display_name is None else display_name,
                    engineering_units='' if point_definition.point_ref.units is None else point_definition.point_ref.units,
                )
            )
        self.services.bindings.bind_signal(
            LogicalSignalBinding(
                logical_signal_id=logical_signal_id,
                source_point_key=point_key,
                binding_policy=binding_policy,
                metadata={
                    'device_identity_key': point_definition.device_identity_key,
                    'point_id': point_definition.point_ref.point_id,
                    'friendly_name': point_definition.friendly_name,
                },
            )
        )
        review = self.services.bindings.build_binding_review(device_identity_key=point_definition.device_identity_key, auto_apply_rebind=False)
        return self._binding_surface(review)

    def register_variable_definition(self, *, definition: VariableDefinition, timestamp: EventTime) -> VariableHealthSummary:
        self.services.variables.register(definition)
        return self.evaluate_variables(timestamp=timestamp, changed_variable_ids=(definition.variable_id,))

    def _publish_bound_signal_snapshots(self, *, poll_result: AdapterPollResult) -> tuple[SignalId, ...]:
        snapshot_map = {snapshot.point.stable_key: snapshot for snapshot in poll_result.snapshots}
        changed_signal_ids: list[SignalId] = []
        total_bound = 0
        for signal_id, binding in tuple(self.services.bindings.signal_bindings.items()):
            snapshot = snapshot_map.get(binding.source_point_key)
            if snapshot is None:
                continue
            total_bound += 1
            if signal_id not in self.services.signals.definitions:
                point_definition = self.services.bindings.point_definitions.get(binding.source_point_key)
                display_name = str(signal_id) if point_definition is None else point_definition.friendly_name
                units = '' if point_definition is None or point_definition.point_ref.units is None else point_definition.point_ref.units
                self.services.signals.register_signal(
                    SignalDefinition(signal_id=signal_id, display_name=display_name, engineering_units=units)
                )
            previous = self.services.signals.snapshots.get(signal_id)
            self.services.signals.publish_snapshot(
                SignalSnapshot(
                    signal_id=signal_id,
                    value=snapshot.engineering_value,
                    quality=snapshot.quality,
                    timestamp=snapshot.received_timestamp,
                )
            )
            if previous is None or previous.value != snapshot.engineering_value or previous.quality != snapshot.quality:
                changed_signal_ids.append(signal_id)
        if self.services.runtime_metrics is not None:
            self.services.runtime_metrics.set_gauge('signals.changed.count', len(changed_signal_ids))
            self.services.runtime_metrics.set_gauge('signals.skipped.count', max(0, total_bound - len(changed_signal_ids)))
        return tuple(changed_signal_ids)

    def evaluate_variables(
        self,
        *,
        timestamp: EventTime,
        changed_signal_ids: tuple[SignalId, ...] = (),
        changed_variable_ids: tuple[VariableId, ...] = (),
    ) -> VariableHealthSummary:
        return self._evaluate_variable_health(
            timestamp=timestamp,
            changed_signal_ids=changed_signal_ids,
            changed_variable_ids=changed_variable_ids,
        )

    def poll_active_adapter(self, *, ui_session: UISessionState, timestamp: EventTime, desired_phase: DeviceLifecyclePhase | None = None) -> PollWorkflowResult:
        adapter_id = ui_session.active_adapter_id
        active_device = ui_session.active_device
        if adapter_id is None or active_device is None:
            lifecycle = self._lifecycle_surface(
                phase=DeviceLifecyclePhase.NO_DEVICE,
                detected_device_count=len(ui_session.detected_devices),
                active_device_key=None,
                active_adapter_id=None,
                projected_point_count=0,
                published_signal_count=binding_summary.resolved_signal_count,
                last_poll_snapshot_count=0,
                disconnected_signal_count=0,
                last_transition='poll_active_adapter',
                needs_review=False,
            )
            return PollWorkflowResult(
                poll_results=(),
                lifecycle_summary=lifecycle,
                binding_review_summary=self._binding_surface(ServiceBindingReviewSummary()),
                variable_health_summary=self._variable_surface(),
            )
        recovery_poll = adapter_id in self.services.adapters.disconnected_adapter_ids
        poll_context = self.services.runtime_metrics.measure('runtime.acquisition.poll.ms') if self.services.runtime_metrics is not None else nullcontext()
        with poll_context:
            result = self.services.adapters.poll_adapter(
                adapter_id=adapter_id,
                timestamp=timestamp,
                include_disconnected=recovery_poll,
            )
        if result is not None:
            self.services.runtime_quality.capture_acquisition(adapter_id=adapter_id, timestamp=timestamp, poll_result=result)
        poll_results = () if result is None else (result,)
        changed_signal_ids = () if result is None else self._publish_bound_signal_snapshots(poll_result=result)
        variable_summary = self.evaluate_variables(timestamp=timestamp, changed_signal_ids=changed_signal_ids)
        binding_summary = self.services.bindings.build_binding_review(device_identity_key=active_device.identity.stable_key, auto_apply_rebind=True)
        lifecycle = self._lifecycle_surface(
            phase=self.services.adapters.lifecycle_phase_for_device(device=active_device, active_adapter_id=adapter_id) if desired_phase is None else desired_phase,
            detected_device_count=len(ui_session.detected_devices),
            active_device_key=active_device.device_key,
            active_adapter_id=adapter_id,
            projected_point_count=len(self.services.bindings.point_definitions_for_device(active_device.identity.stable_key)),
            published_signal_count=binding_summary.resolved_signal_count,
            last_poll_snapshot_count=0 if result is None else len(result.snapshots),
            disconnected_signal_count=0,
            last_transition='poll_active_adapter',
            needs_review=binding_summary.requires_review or variable_summary.impacted_count > 0,
        )
        self.services.runtime_quality.record_processed_cycle(
            timestamp=timestamp,
            lifecycle_summary=lifecycle,
            variable_summary=variable_summary,
            changed_signal_ids=tuple(str(item) for item in changed_signal_ids),
            poll_result=result,
        )
        return PollWorkflowResult(
            poll_results=poll_results,
            lifecycle_summary=lifecycle,
            binding_review_summary=self._binding_surface(binding_summary),
            variable_health_summary=variable_summary,
            reconciliation_summary=self._reconciliation_surface(outcome=None, binding_summary=binding_summary),
        )

    def mark_active_device_disconnected(self, *, ui_session: UISessionState, timestamp: EventTime) -> PollWorkflowResult:
        active_device = ui_session.active_device
        adapter_id = ui_session.active_adapter_id
        if active_device is None or adapter_id is None:
            return self.poll_active_adapter(ui_session=ui_session, timestamp=timestamp)
        self.services.adapters.mark_adapter_disconnected(adapter_id=adapter_id)
        point_keys = self.services.bindings.point_keys_for_device(active_device.identity.stable_key)
        affected_signals = self.services.bindings.affected_signals_for_point_keys(point_keys)
        for signal_id in affected_signals:
            previous = self.services.signals.snapshots.get(signal_id)
            self.services.signals.publish_snapshot(
                SignalSnapshot(
                    signal_id=signal_id,
                    value='' if previous is None else previous.value,
                    quality=SignalQuality.DISCONNECTED,
                    timestamp=timestamp,
                )
            )
        variable_summary = self.evaluate_variables(timestamp=timestamp, changed_signal_ids=affected_signals)
        binding_summary = self.services.bindings.build_binding_review(device_identity_key=active_device.identity.stable_key, auto_apply_rebind=False)
        lifecycle = self._lifecycle_surface(
            phase=DeviceLifecyclePhase.DISCONNECTED,
            detected_device_count=len(ui_session.detected_devices),
            active_device_key=active_device.device_key,
            active_adapter_id=adapter_id,
            projected_point_count=len(self.services.bindings.point_definitions_for_device(active_device.identity.stable_key)),
            published_signal_count=binding_summary.resolved_signal_count,
            last_poll_snapshot_count=0,
            disconnected_signal_count=len(affected_signals),
            last_transition='mark_active_device_disconnected',
            needs_review=True,
        )
        self.services.runtime_quality.record_state_event(
            timestamp=timestamp,
            event_type='device_disconnected',
            attributes={
                'adapter_id': adapter_id,
                'device_key': active_device.device_key,
                'signal_count': len(affected_signals),
            },
        )
        return PollWorkflowResult(
            poll_results=(),
            lifecycle_summary=lifecycle,
            binding_review_summary=self._binding_surface(binding_summary),
            variable_health_summary=variable_summary,
            reconciliation_summary=self._reconciliation_surface(outcome=None, binding_summary=binding_summary),
        )

    def reconnect_active_device(self, *, ui_session: UISessionState, timestamp: EventTime) -> PollWorkflowResult:
        adapter_id = ui_session.active_adapter_id
        active_device = ui_session.active_device
        if adapter_id is not None:
            self.services.adapters.reconnect_adapter(adapter_id=adapter_id)
        if active_device is not None and adapter_id is not None:
            self._project_point_definitions(device=active_device, adapter_id=adapter_id)
            self.services.bindings.build_binding_review(
                device_identity_key=active_device.identity.stable_key,
                auto_apply_rebind=True,
            )
            self.services.runtime_quality.record_state_event(
                timestamp=timestamp,
                event_type='device_reconnected',
                attributes={
                    'adapter_id': adapter_id,
                    'device_key': active_device.device_key,
                },
            )
        desired_phase = DeviceLifecyclePhase.LIVE if ui_session.onboarding_mode == 'quick_start' else DeviceLifecyclePhase.READY_TO_CONFIGURE
        return self.poll_active_adapter(ui_session=ui_session, timestamp=timestamp, desired_phase=desired_phase)

    def build_review_bundle(self, *, ui_session: UISessionState) -> ReviewBundle:
        binding_summary = ui_session.binding_review_summary
        if binding_summary is None and ui_session.active_device is not None:
            binding_summary = self._binding_surface(
                self.services.bindings.build_binding_review(
                    device_identity_key=ui_session.active_device.identity.stable_key,
                    auto_apply_rebind=False,
                )
            )
        elif binding_summary is None:
            binding_summary = self._binding_surface(ServiceBindingReviewSummary())
        lifecycle_summary = ui_session.lifecycle_summary or self._lifecycle_surface(
            phase=ui_session.device_lifecycle_phase,
            detected_device_count=len(ui_session.detected_devices),
            active_device_key=None if ui_session.active_device is None else ui_session.active_device.device_key,
            active_adapter_id=ui_session.active_adapter_id,
            projected_point_count=0,
            published_signal_count=binding_summary.resolved_signal_count,
            last_poll_snapshot_count=0,
            disconnected_signal_count=0,
            last_transition='build_review_bundle',
            needs_review=False,
        )
        variable_summary = ui_session.variable_health_summary or self._variable_surface()
        return ReviewBundle(
            lifecycle_summary=lifecycle_summary,
            binding_review_summary=binding_summary,
            variable_health_summary=variable_summary,
            reconciliation_summary=ui_session.reconciliation_summary,
            workbench_review_state=ui_session.workbench_review_state,
            active_device_key=None if ui_session.active_device is None else ui_session.active_device.device_key,
            active_adapter_id=ui_session.active_adapter_id,
        )
