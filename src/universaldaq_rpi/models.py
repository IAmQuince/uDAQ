from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True, kw_only=True)
class RaspberryPiProbeRow:
    model: str
    host_id: str
    transport: str = 'local'
    firmware_version: str | None = None
    enable_gpio: bool = True
    metadata: Mapping[str, str] = field(default_factory=dict)
