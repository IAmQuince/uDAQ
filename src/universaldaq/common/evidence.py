from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping

from .enums import EvidenceKind
from .ids import EvidenceId
from .timebase import EventTime


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceRecord:
    evidence_id: EvidenceId
    kind: EvidenceKind
    timestamp: EventTime
    summary: str
    attributes: Mapping[str, str] = field(default_factory=dict)
    source_kind: str | None = None
    source_id: str | None = None
    session_id: str | None = None
    actor_id: str | None = None
    origin: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    def with_provenance(
        self,
        *,
        source_kind: str | None = None,
        source_id: str | None = None,
        session_id: str | None = None,
        actor_id: str | None = None,
        origin: str | None = None,
        tags: tuple[str, ...] | None = None,
    ) -> "EvidenceRecord":
        merged_tags = self.tags if tags is None else tuple(dict.fromkeys(self.tags + tags))
        return replace(
            self,
            source_kind=self.source_kind if source_kind is None else source_kind,
            source_id=self.source_id if source_id is None else source_id,
            session_id=self.session_id if session_id is None else session_id,
            actor_id=self.actor_id if actor_id is None else actor_id,
            origin=self.origin if origin is None else origin,
            tags=merged_tags,
        )
