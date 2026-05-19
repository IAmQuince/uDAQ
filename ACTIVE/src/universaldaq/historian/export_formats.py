from __future__ import annotations

import csv
import json
from io import StringIO
from typing import Mapping

from .models import ArtifactManifest, EvidenceBundle, ReviewArtifact


def format_scope_summary(scope_summary: Mapping[str, object]) -> str:
    graph_mode = scope_summary.get('graph_mode', 'unknown')
    pages = ', '.join(str(item) for item in scope_summary.get('selected_pages', [])) or 'none'
    traces = ', '.join(str(item) for item in scope_summary.get('selected_trace_ids', [])) or 'none'
    overlays = ', '.join(str(item) for item in scope_summary.get('overlays', [])) or 'none'
    selected_range = scope_summary.get('selected_range')
    if selected_range is None:
        range_text = 'none'
    else:
        range_text = f"{selected_range[0]}..{selected_range[1]}"
    return (
        f"mode={graph_mode}; pages={pages}; traces={traces}; overlays={overlays}; "
        f"range={range_text}"
    )


def manifest_to_json_payload(manifest: ArtifactManifest) -> dict[str, object]:
    return {
        'manifest_id': manifest.manifest_id,
        'export_id': manifest.export_id,
        'artifact_class': manifest.artifact_class.value,
        'created_at': int(manifest.created_at),
        'created_by_actor': str(manifest.created_by_actor),
        'session_id': manifest.session_id,
        'authority_state': manifest.authority_state.value,
        'review_mode': None if manifest.review_mode is None else manifest.review_mode.value,
        'scope_summary': dict(manifest.scope_summary),
        'artifacts': [
            {
                'artifact_id': descriptor.artifact_id,
                'artifact_type': descriptor.artifact_type,
                'logical_name': descriptor.logical_name,
                'media_type': descriptor.media_type,
                'relative_path': descriptor.relative_path,
                'record_count': descriptor.record_count,
                'metadata': dict(descriptor.metadata),
            }
            for descriptor in manifest.artifacts
        ],
        'omission_notes': list(manifest.omission_notes),
        'warnings': [{'code': item.code, 'message': item.message} for item in manifest.warnings],
    }


def review_artifact_to_markdown(review_artifact: ReviewArtifact) -> str:
    return review_artifact.markdown


def bundle_records_to_csv_rows(bundle: EvidenceBundle) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in bundle.records:
        attributes = dict(record.attributes)
        rows.append(
            {
                'evidence_id': str(record.evidence_id),
                'timestamp': str(record.timestamp),
                'kind': record.kind.value,
                'summary': record.summary,
                'source_kind': '' if record.source_kind is None else record.source_kind,
                'source_id': '' if record.source_id is None else record.source_id,
                'session_id': '' if record.session_id is None else record.session_id,
                'actor_id': '' if record.actor_id is None else record.actor_id,
                'origin': '' if record.origin is None else record.origin,
                'tags': '|'.join(record.tags),
                'attributes_json': json.dumps(attributes, sort_keys=True),
            }
        )
    return rows


def rows_to_csv(rows: list[dict[str, str]]) -> str:
    fieldnames = [
        'evidence_id',
        'timestamp',
        'kind',
        'summary',
        'source_kind',
        'source_id',
        'session_id',
        'actor_id',
        'origin',
        'tags',
        'attributes_json',
    ]
    stream = StringIO()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return stream.getvalue()
