from __future__ import annotations

from dataclasses import dataclass, field

from .export_formats import format_scope_summary
from .models import ArtifactManifest, EvidenceBundle


@dataclass(frozen=True, slots=True, kw_only=True)
class ProofBundleSummary:
    bundle_id: str
    export_id: str | None
    manifest_id: str | None
    record_count: int
    overlay_count: int
    review_mode: str | None
    warning_count: int
    source_counts: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    summaries: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True, kw_only=True)
class ManifestSummary:
    manifest_id: str
    export_id: str
    artifact_class: str
    artifact_count: int
    warning_count: int
    scope_text: str
    omission_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class BundleInventory:
    bundle_id: str
    record_ids: tuple[str, ...]
    source_kinds: tuple[str, ...]


def summarize_bundle(bundle: EvidenceBundle) -> ProofBundleSummary:
    return ProofBundleSummary(
        bundle_id=bundle.bundle_id,
        export_id=bundle.export_id,
        manifest_id=bundle.manifest_id,
        record_count=len(bundle.records),
        overlay_count=len(bundle.overlays),
        review_mode=None if bundle.review_mode is None else bundle.review_mode.value,
        warning_count=len(bundle.warnings),
        source_counts=bundle.source_counts,
        summaries=bundle.summaries(),
    )


def summarize_manifest(manifest: ArtifactManifest) -> ManifestSummary:
    return ManifestSummary(
        manifest_id=manifest.manifest_id,
        export_id=manifest.export_id,
        artifact_class=manifest.artifact_class.value,
        artifact_count=len(manifest.artifacts),
        warning_count=len(manifest.warnings),
        scope_text=format_scope_summary(manifest.scope_summary),
        omission_count=len(manifest.omission_notes),
    )


def build_bundle_inventory(bundle: EvidenceBundle) -> BundleInventory:
    return BundleInventory(
        bundle_id=bundle.bundle_id,
        record_ids=tuple(str(record.evidence_id) for record in bundle.records),
        source_kinds=tuple('unknown' if record.source_kind is None else record.source_kind for record in bundle.records),
    )
