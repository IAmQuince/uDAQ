from __future__ import annotations

from dataclasses import dataclass, field

from universaldaq.common import AuthorizationState, EventTime
from universaldaq.security import AuthorizationDecision

from .arbiter import OutputArbiter
from .models import CommandTrace, OutputRequest


@dataclass(slots=True)
class OutputCommandService:
    traces: list[CommandTrace] = field(default_factory=list)

    def submit(
        self,
        *,
        request: OutputRequest,
        authorization_state: AuthorizationState | None = None,
        authorization_decision: AuthorizationDecision | None = None,
        applied_value: str | None = None,
        observed_value: str | None = None,
        applied_at: EventTime | None = None,
        observed_at: EventTime | None = None,
    ) -> CommandTrace:
        trace = OutputArbiter.issue_trace(
            request=request,
            authorization_state=authorization_state,
            authorization_decision=authorization_decision,
            applied_value=applied_value,
            observed_value=observed_value,
            applied_at=applied_at,
            observed_at=observed_at,
        )
        self.traces.append(trace)
        return trace

    def latest_for_output(self, output_id: str) -> CommandTrace | None:
        for trace in reversed(self.traces):
            if str(trace.request.output_id) == output_id:
                return trace
        return None

    def attach_adapter_result(self, *, request_id: str, adapter_result) -> CommandTrace | None:
        for idx in range(len(self.traces) - 1, -1, -1):
            trace = self.traces[idx]
            if str(trace.request.request_id) == request_id:
                updated = trace.with_adapter_result(adapter_result)
                self.traces[idx] = updated
                return updated
        return None
