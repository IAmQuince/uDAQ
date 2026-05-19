from __future__ import annotations

from dataclasses import dataclass, replace

from universaldaq.common import SignalId, SignalQuality


@dataclass(frozen=True, slots=True, kw_only=True)
class SignalDefinition:
    signal_id: SignalId
    display_name: str
    engineering_units: str
    quality: SignalQuality = SignalQuality.GOOD

    def renamed(self, new_display_name: str) -> "SignalDefinition":
        return replace(self, display_name=new_display_name)


@dataclass(frozen=True, slots=True, kw_only=True)
class DerivedSignalDefinition(SignalDefinition):
    dependencies: tuple[SignalId, ...]
    expression: str
