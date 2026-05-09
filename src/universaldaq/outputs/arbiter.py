from __future__ import annotations

from dataclasses import dataclass

from universaldaq.common import ActorId, AuthorizationState, EventTime, OutputId, RequestId
from universaldaq.security import AuthorizationDecision

from .models import CommandTrace, CommandTraceFactory, OutputRequest


@dataclass(frozen=True, slots=True, kw_only=True)
class ArbitrationOutcome:
    authorization_state: AuthorizationState
    allowed: bool
    phase: str
    reason: str | None = None
    reason_code: str | None = None


class OutputArbiter:
    @staticmethod
    def decide(
        *,
        authorization_decision: AuthorizationDecision | None = None,
        authorization_state: AuthorizationState | None = None,
        requested_value: str,
    ) -> ArbitrationOutcome:
        del requested_value
        if authorization_decision is not None and not authorization_decision.allowed:
            return ArbitrationOutcome(
                authorization_state=authorization_decision.authorization_state,
                allowed=False,
                phase='authorization',
                reason=authorization_decision.reason_text,
                reason_code=authorization_decision.reason_code.value,
            )
        state = AuthorizationState.ALLOWED if authorization_state is None else authorization_state
        if state == AuthorizationState.ALLOWED:
            return ArbitrationOutcome(authorization_state=state, allowed=True, phase='authorized')
        if state == AuthorizationState.VIEW_ONLY:
            return ArbitrationOutcome(
                authorization_state=state,
                allowed=False,
                phase='authorization',
                reason='view-only session cannot publish apply state',
                reason_code='legacy_view_only',
            )
        return ArbitrationOutcome(
            authorization_state=state,
            allowed=False,
            phase='authorization',
            reason='authorization denied for output command',
            reason_code='legacy_denied',
        )

    @staticmethod
    def build_request(
        *,
        request_id: RequestId,
        output_id: OutputId,
        requested_value: str,
        actor: ActorId,
        requested_at: EventTime,
    ) -> OutputRequest:
        return OutputRequest(
            request_id=request_id,
            output_id=output_id,
            requested_value=requested_value,
            actor=actor,
            requested_at=requested_at,
        )

    @staticmethod
    def issue_trace(
        *,
        request: OutputRequest,
        authorization_state: AuthorizationState | None = None,
        authorization_decision: AuthorizationDecision | None = None,
        applied_value: str | None,
        observed_value: str | None,
        applied_at: EventTime | None,
        observed_at: EventTime | None,
    ) -> CommandTrace:
        outcome = OutputArbiter.decide(
            authorization_state=authorization_state,
            authorization_decision=authorization_decision,
            requested_value=request.requested_value,
        )
        if not outcome.allowed:
            if authorization_decision is not None:
                return CommandTraceFactory.authorization_denied(request=request, decision=authorization_decision)
            return CommandTraceFactory.arbitration_blocked(
                request=request,
                reason=outcome.reason or 'blocked',
                authorization_state=outcome.authorization_state,
            )
        if applied_value is None or observed_value is None or applied_at is None or observed_at is None:
            return CommandTraceFactory.arbitration_blocked(
                request=request,
                reason='allowed request requires applied and observed values in the bounded shell slice',
                authorization_state=outcome.authorization_state,
                authorization_decision=authorization_decision,
            )
        return CommandTraceFactory.applied_then_observed(
            request=request,
            applied_value=applied_value,
            observed_value=observed_value,
            applied_at=applied_at,
            observed_at=observed_at,
            authorization_decision=authorization_decision,
        )
