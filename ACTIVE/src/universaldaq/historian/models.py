from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.common import ActorId, AuthorizationState, EvidenceRecord, EventTime, ExportArtifactClass, GraphMode
from universaldaq.security import AuthorizationDecision


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportScope:
    graph_mode: GraphMode
    selected_range: tuple[EventTime, EventTime] | None = None
    selected_pages: tuple[str, ...] = field(default_factory=tuple)
    selected_trace_ids: tuple[str, ...] = field(default_factory=tuple)
    overlays: tuple[str, ...] = field(default_factory=tuple)
    include_commands: bool = True
    include_alarms: bool = True
    include_restores: bool = True
    include_shell_evidence: bool = True
    include_profiles: bool = False
    include_diagnostics: bool = False

    def summary(self) -> dict[str, object]:
        return {
            'graph_mode': self.graph_mode.value,
            'selected_range': None if self.selected_range is None else [int(self.selected_range[0]), int(self.selected_range[1])],
            'selected_pages': list(self.selected_pages),
            'selected_trace_ids': list(self.selected_trace_ids),
            'overlays': list(self.overlays),
            'include_commands': self.include_commands,
            'include_alarms': self.include_alarms,
            'include_restores': self.include_restores,
            'include_shell_evidence': self.include_shell_evidence,
            'include_profiles': self.include_profiles,
            'include_diagnostics': self.include_diagnostics,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportIntent:
    export_id: str
    artifact_class: ExportArtifactClass
    requested_by_actor: ActorId
    session_id: str
    requested_at: EventTime
    authority_state: AuthorizationState
    origin: str = 'local-shell'
    scope: ExportScope


@dataclass(frozen=True, slots=True, kw_only=True)
class BundleIntegrityWarning:
    code: str
    message: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactDescriptor:
    artifact_id: str
    artifact_type: str
    logical_name: str
    media_type: str
    relative_path: str
    record_count: int = 0
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactManifest:
    manifest_id: str
    export_id: str
    artifact_class: ExportArtifactClass
    created_at: EventTime
    created_by_actor: ActorId
    session_id: str
    authority_state: AuthorizationState
    review_mode: GraphMode | None
    scope_summary: Mapping[str, object]
    artifacts: tuple[ArtifactDescriptor, ...] = field(default_factory=tuple)
    omission_notes: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[BundleIntegrityWarning, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewArtifact:
    artifact_id: str
    logical_name: str
    markdown: str
    summary_lines: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True, kw_only=True)
class SerializedArtifact:
    descriptor: ArtifactDescriptor
    content: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceBundle:
    bundle_id: str
    records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)
    overlays: tuple[str, ...] = field(default_factory=tuple)
    review_mode: GraphMode | None = None
    export_id: str | None = None
    manifest_id: str | None = None
    source_counts: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    warnings: tuple[BundleIntegrityWarning, ...] = field(default_factory=tuple)

    def summaries(self) -> tuple[str, ...]:
        return tuple(record.summary for record in self.records)


@dataclass(frozen=True, slots=True, kw_only=True)
class BundleBuildResult:
    export_intent: ExportIntent
    bundle: EvidenceBundle
    manifest: ArtifactManifest
    review_artifact: ReviewArtifact | None = None
    serialized_artifacts: tuple[SerializedArtifact, ...] = field(default_factory=tuple)
    warnings: tuple[BundleIntegrityWarning, ...] = field(default_factory=tuple)
    authorization_decision: AuthorizationDecision | None = None
