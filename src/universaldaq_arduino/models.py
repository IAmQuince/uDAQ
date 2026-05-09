from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True, kw_only=True)
class ArduinoProbeRow:
    board: str
    serial_number: str
    port: str = 'auto'
    transport: str = 'serial'
    firmware_version: str | None = None
    connection_label: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)
