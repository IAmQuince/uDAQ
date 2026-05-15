from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidationFinding:
    code: str
    message: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidationReport:
    findings: tuple[ValidationFinding, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return not self.findings
