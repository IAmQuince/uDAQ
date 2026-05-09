from __future__ import annotations

from universaldaq.common import ValidationFinding, ValidationReport
from .models import CommandTrace


def validate_command_trace(trace: CommandTrace) -> ValidationReport:
    findings: list[ValidationFinding] = []
    if trace.decision == trace.decision.BLOCKED and trace.apply_published:
        findings.append(ValidationFinding(code="blocked_apply", message="blocked trace published apply state"))
    if trace.apply_published and trace.applied_state is not None and trace.applied_state.published_at < trace.request.requested_at:
        findings.append(ValidationFinding(code="apply_before_request", message="apply published before request"))
    if trace.observed_state is not None and trace.applied_state is not None:
        if trace.observed_state.observed_at < trace.applied_state.published_at:
            findings.append(ValidationFinding(code="observe_before_apply", message="observed state precedes apply publication"))
    return ValidationReport(findings=tuple(findings))
