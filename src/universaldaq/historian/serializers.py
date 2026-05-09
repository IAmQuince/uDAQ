from __future__ import annotations

import json

from .export_formats import bundle_records_to_csv_rows, manifest_to_json_payload, review_artifact_to_markdown, rows_to_csv
from .models import ArtifactManifest, EvidenceBundle, ReviewArtifact


def serialize_manifest_json(manifest: ArtifactManifest) -> str:
    return json.dumps(manifest_to_json_payload(manifest), indent=2, sort_keys=True)


def serialize_review_artifact_markdown(review_artifact: ReviewArtifact) -> str:
    return review_artifact_to_markdown(review_artifact)


def serialize_bundle_records_csv(bundle: EvidenceBundle) -> str:
    return rows_to_csv(bundle_records_to_csv_rows(bundle))


def serialize_json_payload(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)
