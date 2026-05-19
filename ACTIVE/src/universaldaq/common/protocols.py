from __future__ import annotations

from typing import Protocol

from .evidence import EvidenceRecord


class EvidenceEmitter(Protocol):
    def evidence(self) -> tuple[EvidenceRecord, ...]:
        ...
