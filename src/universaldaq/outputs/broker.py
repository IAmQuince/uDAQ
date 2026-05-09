from __future__ import annotations

from dataclasses import dataclass, field

from universaldaq.adapters import AdapterCommandRequest, AdapterCommandResult, AdapterManagerService
from universaldaq.common import ActorId, AuthorizationState, EventTime, OutputId, RequestId, as_event_time

from .arbiter import OutputArbiter
from .models import (
    BrokerEvent,
    CommandExecutionResult,
    CommandTraceFactory,
    OwnershipLease,
    SafeStatePolicy,
    WritableTagBinding,
)
from .services import OutputCommandService


@dataclass(slots=True)
class CommandArbitrationBroker:
    adapter_manager: AdapterManagerService
    output_service: OutputCommandService
    bindings: dict[str, WritableTagBinding] = field(default_factory=dict)
    leases: dict[str, OwnershipLease] = field(default_factory=dict)
    unavailable_outputs: set[str] = field(default_factory=set)
    events: list[BrokerEvent] = field(default_factory=list)

    def register_binding(self, binding: WritableTagBinding) -> None:
        self.bindings[str(binding.output_id)] = binding

    def binding_inventory(self) -> tuple[WritableTagBinding, ...]:
        return tuple(self.bindings[key] for key in sorted(self.bindings.keys()))

    def active_leases(self, *, timestamp: EventTime) -> tuple[OwnershipLease, ...]:
        self._expire_stale_leases(timestamp=timestamp)
        return tuple(self.leases[key] for key in sorted(self.leases.keys()))

    def set_output_availability(
        self,
        *,
        output_id: OutputId,
        available: bool,
        timestamp: EventTime,
        summary: str,
        clear_lease_on_restore: bool = True,
    ) -> tuple[BrokerEvent, ...]:
        key = str(output_id)
        emitted: list[BrokerEvent] = []
        if available:
            self.unavailable_outputs.discard(key)
            emitted.append(self._append_event(event_type='target_restored', output_id=output_id, timestamp=timestamp, summary=summary))
            if clear_lease_on_restore:
                lease = self.leases.pop(key, None)
                if lease is not None:
                    emitted.append(
                        self._append_event(
                            event_type='lease_cleared_on_restore',
                            output_id=output_id,
                            timestamp=timestamp,
                            owner=lease.owner,
                            summary='restored target cleared prior ownership lease',
                        )
                    )
            return tuple(emitted)
        self.unavailable_outputs.add(key)
        emitted.append(self._append_event(event_type='target_degraded', output_id=output_id, timestamp=timestamp, summary=summary))
        lease = self.leases.pop(key, None)
        if lease is not None:
            emitted.append(
                self._append_event(
                    event_type='lease_revoked_on_degrade',
                    output_id=output_id,
                    timestamp=timestamp,
                    owner=lease.owner,
                    summary='degraded target revoked the active writer lease',
                    metadata={'prior_lease_expires_at': str(lease.expires_at)},
                )
            )
        binding = self.bindings.get(key)
        if binding is not None and binding.safe_state_policy == SafeStatePolicy.RETURN_TO_SAFE and binding.safe_state_value is not None:
            emitted.append(
                self._append_event(
                    event_type='safe_state_required',
                    output_id=output_id,
                    timestamp=timestamp,
                    summary='target degraded and safe state required',
                    metadata={'safe_state_value': binding.safe_state_value},
                )
            )
        return tuple(emitted)

    def issue_command(
        self,
        *,
        request_id: RequestId,
        output_id: OutputId,
        requested_value: str,
        actor: ActorId,
        requested_at: EventTime,
        lease_duration_ticks: int = 3,
    ) -> CommandExecutionResult:
        self._expire_stale_leases(timestamp=requested_at)
        request = OutputArbiter.build_request(
            request_id=request_id,
            output_id=output_id,
            requested_value=requested_value,
            actor=actor,
            requested_at=requested_at,
        )
        binding = self.bindings.get(str(output_id))
        if binding is None:
            trace = CommandTraceFactory.blocked(request=request, reason='target is not registered as writable')
            self.output_service.traces.append(trace)
            event = self._append_event(
                event_type='command_rejected_invalid_target',
                output_id=output_id,
                timestamp=requested_at,
                owner=actor,
                summary='command rejected because writable target is unknown',
            )
            return CommandExecutionResult(trace=trace, disposition='invalid_target', broker_events=(event,))
        if str(output_id) in self.unavailable_outputs:
            trace = CommandTraceFactory.blocked(request=request, reason='target is currently degraded or unavailable')
            self.output_service.traces.append(trace)
            event = self._append_event(
                event_type='command_rejected_unavailable',
                output_id=output_id,
                timestamp=requested_at,
                owner=actor,
                summary='command rejected because target is unavailable',
            )
            return CommandExecutionResult(trace=trace, disposition='target_unavailable', broker_events=(event,))
        active_lease = self.leases.get(str(output_id))
        same_owner_active = active_lease is not None and active_lease.is_active(timestamp=requested_at) and active_lease.owner == actor
        if active_lease is not None and active_lease.is_active(timestamp=requested_at) and active_lease.owner != actor:
            trace = CommandTraceFactory.arbitration_blocked(
                request=request,
                reason='ownership conflict with an active writer lease',
                authorization_state=AuthorizationState.ALLOWED,
            )
            self.output_service.traces.append(trace)
            event = self._append_event(
                event_type='command_rejected_ownership_conflict',
                output_id=output_id,
                timestamp=requested_at,
                owner=actor,
                summary='command rejected because another owner currently holds the writable lease',
                metadata={'active_owner': str(active_lease.owner)},
            )
            return CommandExecutionResult(trace=trace, disposition='ownership_conflict', lease=active_lease, broker_events=(event,))

        trace = self.output_service.submit(
            request=request,
            authorization_state=AuthorizationState.ALLOWED,
            applied_value=requested_value,
            observed_value=requested_value,
            applied_at=requested_at,
            observed_at=requested_at,
        )
        adapter_request = AdapterCommandRequest(
            adapter_id=binding.adapter_id,
            point_id=binding.point_id,
            request_id=request_id,
            output_id=output_id,
            requested_value=requested_value,
            requested_at=requested_at,
            actor_id=actor,
            authorization_decision=None,
        )
        adapter_result = self.adapter_manager.submit_command(adapter_request)
        updated_trace = self.output_service.attach_adapter_result(request_id=str(request_id), adapter_result=adapter_result)
        if updated_trace is None:
            updated_trace = trace.with_adapter_result(adapter_result)
        emitted: list[BrokerEvent] = [
            self._append_event(
                event_type='command_intent',
                output_id=output_id,
                timestamp=requested_at,
                owner=actor,
                summary='command intent admitted for bounded adapter dispatch',
                metadata={'requested_value': requested_value},
            )
        ]
        lease: OwnershipLease | None = None
        if adapter_result.successful:
            lease = OwnershipLease(
                output_id=output_id,
                owner=actor,
                acquired_at=requested_at,
                expires_at=as_event_time(int(requested_at) + max(1, int(lease_duration_ticks))),
            )
            self.leases[str(output_id)] = lease
            emitted.append(
                self._append_event(
                    event_type='ownership_renewed' if same_owner_active else 'ownership_granted',
                    output_id=output_id,
                    timestamp=requested_at,
                    owner=actor,
                    summary='writer lease renewed for same-owner superseding command' if same_owner_active else 'writer lease granted for accepted command',
                    metadata={
                        'lease_expires_at': str(lease.expires_at),
                        **({} if active_lease is None else {'prior_lease_expires_at': str(active_lease.expires_at)}),
                    },
                )
            )
            disposition = 'accepted'
        else:
            disposition = 'adapter_failed'
            emitted.append(
                self._append_event(
                    event_type='command_failed',
                    output_id=output_id,
                    timestamp=requested_at,
                    owner=actor,
                    summary='adapter reported a bounded command failure',
                    metadata={'adapter_outcome': adapter_result.outcome.value, 'reason': '' if adapter_result.reason is None else adapter_result.reason},
                )
            )
            if binding.safe_state_policy == SafeStatePolicy.RETURN_TO_SAFE and binding.safe_state_value is not None:
                emitted.append(
                    self._append_event(
                        event_type='safe_state_required',
                        output_id=output_id,
                        timestamp=requested_at,
                        owner=actor,
                        summary='command failure requires explicit safe state review',
                        metadata={'safe_state_value': binding.safe_state_value},
                    )
                )
        return CommandExecutionResult(
            trace=updated_trace,
            disposition=disposition,
            lease=lease,
            adapter_result=adapter_result,
            broker_events=tuple(emitted),
        )

    def _expire_stale_leases(self, *, timestamp: EventTime) -> None:
        expired_keys = [key for key, lease in self.leases.items() if not lease.is_active(timestamp=timestamp)]
        for key in expired_keys:
            lease = self.leases.pop(key)
            self._append_event(
                event_type='lease_expired',
                output_id=lease.output_id,
                timestamp=timestamp,
                owner=lease.owner,
                summary='writer lease expired before the next command attempt',
            )

    def _append_event(
        self,
        *,
        event_type: str,
        output_id: OutputId,
        timestamp: EventTime,
        summary: str,
        owner: ActorId | None = None,
        metadata: dict[str, str] | None = None,
    ) -> BrokerEvent:
        event = BrokerEvent(
            event_type=event_type,
            output_id=output_id,
            timestamp=timestamp,
            summary=summary,
            owner=owner,
            metadata={} if metadata is None else dict(metadata),
        )
        self.events.append(event)
        return event
