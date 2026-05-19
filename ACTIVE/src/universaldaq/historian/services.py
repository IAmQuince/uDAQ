from __future__ import annotations

from dataclasses import dataclass, field

from universaldaq.common import ActorId, AuthorizationState, EvidenceRecord, ExportArtifactClass, GraphMode, as_event_time
from universaldaq.events import AlarmLifecycle
from universaldaq.outputs import CommandTrace
from universaldaq.profiles import ProfileSnapshot, RestoreResult
from universaldaq.profiles.serializers import serialize_profile_snapshots_for_export

from .models import (
    ArtifactDescriptor,
    ArtifactManifest,
    BundleBuildResult,
    BundleIntegrityWarning,
    EvidenceBundle,
    ExportIntent,
    ExportScope,
    ReviewArtifact,
    SerializedArtifact,
)
from .serializers import serialize_bundle_records_csv, serialize_json_payload, serialize_manifest_json, serialize_review_artifact_markdown


@dataclass(slots=True)
class EvidenceBundleService:
    bundles: list[EvidenceBundle] = field(default_factory=list)
    manifests: list[ArtifactManifest] = field(default_factory=list)
    export_results: list[BundleBuildResult] = field(default_factory=list)

    def resolve_export_scope(
        self,
        *,
        graph_mode: GraphMode,
        selected_range: tuple[int, int] | None = None,
        selected_pages: tuple[str, ...] = (),
        selected_trace_ids: tuple[str, ...] = (),
        overlays: tuple[str, ...] = (),
        include_commands: bool = True,
        include_alarms: bool = True,
        include_restores: bool = True,
        include_shell_evidence: bool = True,
        include_profiles: bool = False,
        include_diagnostics: bool = False,
    ) -> ExportScope:
        normalized_range = None if selected_range is None else (as_event_time(int(selected_range[0])), as_event_time(int(selected_range[1])))
        return ExportScope(
            graph_mode=graph_mode,
            selected_range=normalized_range,
            selected_pages=selected_pages,
            selected_trace_ids=selected_trace_ids,
            overlays=overlays,
            include_commands=include_commands,
            include_alarms=include_alarms,
            include_restores=include_restores,
            include_shell_evidence=include_shell_evidence,
            include_profiles=include_profiles,
            include_diagnostics=include_diagnostics,
        )

    def build_export_intent(
        self,
        *,
        export_id: str,
        artifact_class: ExportArtifactClass,
        requested_by_actor: ActorId,
        session_id: str,
        requested_at: int,
        authority_state: AuthorizationState,
        scope: ExportScope,
        origin: str = 'local-shell',
    ) -> ExportIntent:
        return ExportIntent(
            export_id=export_id,
            artifact_class=artifact_class,
            requested_by_actor=requested_by_actor,
            session_id=session_id,
            requested_at=as_event_time(int(requested_at)),
            authority_state=authority_state,
            origin=origin,
            scope=scope,
        )

    def _enrich_records(
        self,
        records: tuple[EvidenceRecord, ...],
        *,
        intent: ExportIntent,
        source_kind: str,
        source_id: str,
        actor_id: str | None = None,
        origin: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> tuple[EvidenceRecord, ...]:
        return tuple(
            record.with_provenance(
                source_kind=source_kind,
                source_id=source_id,
                session_id=intent.session_id,
                actor_id=record.actor_id if record.actor_id is not None else actor_id,
                origin=record.origin if record.origin is not None else (intent.origin if origin is None else origin),
                tags=tags,
            )
            for record in records
        )

    def collect_records(
        self,
        *,
        intent: ExportIntent,
        command_traces: tuple[CommandTrace, ...] = (),
        restore_results: tuple[RestoreResult, ...] = (),
        alarm_lifecycles: tuple[AlarmLifecycle, ...] = (),
        session_records: tuple[EvidenceRecord, ...] = (),
    ) -> tuple[tuple[EvidenceRecord, ...], tuple[tuple[str, int], ...], tuple[str, ...], tuple[BundleIntegrityWarning, ...]]:
        records: list[EvidenceRecord] = []
        source_counts: list[tuple[str, int]] = []
        omission_notes: list[str] = []
        warnings: list[BundleIntegrityWarning] = []

        def include_family(name: str, enabled: bool, count: int) -> None:
            if not enabled:
                omission_notes.append(f'{name} omitted by export scope')
            elif count == 0:
                warnings.append(BundleIntegrityWarning(code=f'empty_{name}', message=f'No {name} were available for export scope'))

        if intent.scope.include_commands:
            count_before = len(records)
            for trace in command_traces:
                records.extend(
                    self._enrich_records(
                        trace.evidence_records,
                        intent=intent,
                        source_kind='command_trace',
                        source_id=str(trace.request.request_id),
                        actor_id=str(trace.request.actor),
                        tags=('commands',),
                    )
                )
            source_counts.append(('commands', len(records) - count_before))
            include_family('commands', True, len(records) - count_before)
        else:
            include_family('commands', False, 0)

        if intent.scope.include_restores:
            count_before = len(records)
            for restore in restore_results:
                source_id = str(restore.profile_id) if restore.profile_id is not None else 'restore'
                records.extend(
                    self._enrich_records(
                        restore.evidence_records,
                        intent=intent,
                        source_kind='restore',
                        source_id=source_id,
                        origin=restore.origin.value,
                        tags=('restore',),
                    )
                )
            source_counts.append(('restores', len(records) - count_before))
            include_family('restores', True, len(records) - count_before)
        else:
            include_family('restores', False, 0)

        if intent.scope.include_alarms:
            count_before = len(records)
            for lifecycle in alarm_lifecycles:
                records.extend(
                    self._enrich_records(
                        lifecycle.evidence_records,
                        intent=intent,
                        source_kind='alarm_lifecycle',
                        source_id=str(lifecycle.alarm_id),
                        tags=('alarms',),
                    )
                )
            source_counts.append(('alarms', len(records) - count_before))
            include_family('alarms', True, len(records) - count_before)
        else:
            include_family('alarms', False, 0)

        if intent.scope.include_shell_evidence:
            count_before = len(records)
            records.extend(
                self._enrich_records(
                    session_records,
                    intent=intent,
                    source_kind='shell_session',
                    source_id=intent.session_id,
                    actor_id=str(intent.requested_by_actor),
                    tags=('shell',),
                )
            )
            source_counts.append(('shell_evidence', len(records) - count_before))
            include_family('shell_evidence', True, len(records) - count_before)
        else:
            include_family('shell_evidence', False, 0)

        if not records:
            warnings.append(BundleIntegrityWarning(code='empty_scope', message='Export scope resolved to no records'))
        return tuple(records), tuple(source_counts), tuple(omission_notes), tuple(warnings)

    def build_review_artifact(
        self,
        *,
        artifact_id: str,
        manifest_id: str,
        intent: ExportIntent,
        bundle: EvidenceBundle,
        omission_notes: tuple[str, ...],
    ) -> ReviewArtifact:
        lines = [
            '# UniversalDAQ Review Artifact',
            '',
            f'- export_id: {intent.export_id}',
            f'- manifest_id: {manifest_id}',
            f'- artifact_class: {intent.artifact_class.value}',
            f'- requested_by: {intent.requested_by_actor}',
            f'- session_id: {intent.session_id}',
            f'- authority_state: {intent.authority_state.value}',
            f'- review_mode: {bundle.review_mode.value if bundle.review_mode is not None else "none"}',
            f'- record_count: {len(bundle.records)}',
            '',
            '## Scope',
            '',
            f'- graph_mode: {intent.scope.graph_mode.value}',
            f'- selected_pages: {", ".join(intent.scope.selected_pages) or "none"}',
            f'- selected_traces: {", ".join(intent.scope.selected_trace_ids) or "none"}',
            f'- overlays: {", ".join(intent.scope.overlays) or "none"}',
            f'- selected_range: {"none" if intent.scope.selected_range is None else f"{intent.scope.selected_range[0]}..{intent.scope.selected_range[1]}"}',
            '',
            '## Source counts',
            '',
        ]
        for family, count in bundle.source_counts:
            lines.append(f'- {family}: {count}')
        if omission_notes:
            lines.extend(['', '## Omission notes', ''])
            lines.extend(f'- {note}' for note in omission_notes)
        if bundle.warnings:
            lines.extend(['', '## Warnings', ''])
            lines.extend(f'- {warning.code}: {warning.message}' for warning in bundle.warnings)
        lines.extend(['', '## Evidence summaries', ''])
        lines.extend(f'- {summary}' for summary in bundle.summaries())
        return ReviewArtifact(
            artifact_id=artifact_id,
            logical_name='review_summary',
            markdown='\n'.join(lines) + '\n',
            summary_lines=tuple(lines),
        )

    def build_manifest(
        self,
        *,
        manifest_id: str,
        intent: ExportIntent,
        review_mode: GraphMode | None,
        artifacts: tuple[ArtifactDescriptor, ...],
        omission_notes: tuple[str, ...],
        warnings: tuple[BundleIntegrityWarning, ...],
    ) -> ArtifactManifest:
        return ArtifactManifest(
            manifest_id=manifest_id,
            export_id=intent.export_id,
            artifact_class=intent.artifact_class,
            created_at=intent.requested_at,
            created_by_actor=intent.requested_by_actor,
            session_id=intent.session_id,
            authority_state=intent.authority_state,
            review_mode=review_mode,
            scope_summary=intent.scope.summary(),
            artifacts=artifacts,
            omission_notes=omission_notes,
            warnings=warnings,
        )

    def serialize_bundle_payloads(
        self,
        *,
        manifest: ArtifactManifest,
        bundle: EvidenceBundle,
        review_artifact: ReviewArtifact | None = None,
        profile_snapshots: tuple[ProfileSnapshot, ...] = (),
        diagnostics: tuple[dict[str, object], ...] = (),
    ) -> tuple[SerializedArtifact, ...]:
        payloads: list[SerializedArtifact] = []
        manifest_descriptor = ArtifactDescriptor(
            artifact_id=f'{manifest.manifest_id}-JSON',
            artifact_type='manifest',
            logical_name='manifest_json',
            media_type='application/json',
            relative_path='manifest.json',
            metadata={'export_id': manifest.export_id},
        )
        payloads.append(SerializedArtifact(descriptor=manifest_descriptor, content=serialize_manifest_json(manifest)))

        records_descriptor = ArtifactDescriptor(
            artifact_id=f'{bundle.bundle_id}-CSV',
            artifact_type='evidence_records',
            logical_name='evidence_records_csv',
            media_type='text/csv',
            relative_path='records.csv',
            record_count=len(bundle.records),
            metadata={'bundle_id': bundle.bundle_id},
        )
        payloads.append(SerializedArtifact(descriptor=records_descriptor, content=serialize_bundle_records_csv(bundle)))

        if review_artifact is not None:
            review_descriptor = ArtifactDescriptor(
                artifact_id=review_artifact.artifact_id,
                artifact_type='review_artifact',
                logical_name=review_artifact.logical_name,
                media_type='text/markdown',
                relative_path='review.md',
                record_count=len(bundle.records),
                metadata={'manifest_id': manifest.manifest_id},
            )
            payloads.append(SerializedArtifact(descriptor=review_descriptor, content=serialize_review_artifact_markdown(review_artifact)))

        if profile_snapshots:
            profiles_descriptor = ArtifactDescriptor(
                artifact_id=f'{manifest.manifest_id}-PROFILES',
                artifact_type='profile_snapshots',
                logical_name='profiles_json',
                media_type='application/json',
                relative_path='profiles.json',
                record_count=len(profile_snapshots),
                metadata={'included_profiles': str(len(profile_snapshots))},
            )
            profiles_payload = serialize_profile_snapshots_for_export(profile_snapshots)
            payloads.append(SerializedArtifact(descriptor=profiles_descriptor, content=serialize_json_payload(profiles_payload)))

        if diagnostics:
            diagnostics_descriptor = ArtifactDescriptor(
                artifact_id=f'{manifest.manifest_id}-DIAG',
                artifact_type='diagnostic_snapshot',
                logical_name='diagnostics_json',
                media_type='application/json',
                relative_path='diagnostics.json',
                record_count=len(diagnostics),
                metadata={'included_snapshots': str(len(diagnostics))},
            )
            payloads.append(SerializedArtifact(descriptor=diagnostics_descriptor, content=serialize_json_payload(list(diagnostics))))

        return tuple(payloads)

    def build_bundle_from_intent(
        self,
        *,
        intent: ExportIntent,
        bundle_id: str,
        manifest_id: str,
        command_traces: tuple[CommandTrace, ...] = (),
        restore_results: tuple[RestoreResult, ...] = (),
        alarm_lifecycles: tuple[AlarmLifecycle, ...] = (),
        session_records: tuple[EvidenceRecord, ...] = (),
        overlays: tuple[str, ...] = (),
        profile_snapshots: tuple[ProfileSnapshot, ...] = (),
        diagnostics: tuple[dict[str, object], ...] = (),
    ) -> BundleBuildResult:
        records, source_counts, omission_notes, warnings = self.collect_records(
            intent=intent,
            command_traces=command_traces,
            restore_results=restore_results,
            alarm_lifecycles=alarm_lifecycles,
            session_records=session_records,
        )
        bundle = EvidenceBundle(
            bundle_id=bundle_id,
            records=records,
            overlays=overlays,
            review_mode=intent.scope.graph_mode,
            export_id=intent.export_id,
            manifest_id=manifest_id,
            source_counts=source_counts,
            warnings=warnings,
        )
        review_artifact = self.build_review_artifact(
            artifact_id=f'{manifest_id}-REVIEW',
            manifest_id=manifest_id,
            intent=intent,
            bundle=bundle,
            omission_notes=omission_notes,
        )
        temporary_artifacts = (
            ArtifactDescriptor(
                artifact_id=f'{manifest_id}-JSON',
                artifact_type='manifest',
                logical_name='manifest_json',
                media_type='application/json',
                relative_path='manifest.json',
            ),
            ArtifactDescriptor(
                artifact_id=f'{bundle.bundle_id}-CSV',
                artifact_type='evidence_records',
                logical_name='evidence_records_csv',
                media_type='text/csv',
                relative_path='records.csv',
                record_count=len(bundle.records),
            ),
            ArtifactDescriptor(
                artifact_id=review_artifact.artifact_id,
                artifact_type='review_artifact',
                logical_name=review_artifact.logical_name,
                media_type='text/markdown',
                relative_path='review.md',
                record_count=len(bundle.records),
            ),
        )
        if profile_snapshots:
            temporary_artifacts += (
                ArtifactDescriptor(
                    artifact_id=f'{manifest_id}-PROFILES',
                    artifact_type='profile_snapshots',
                    logical_name='profiles_json',
                    media_type='application/json',
                    relative_path='profiles.json',
                    record_count=len(profile_snapshots),
                ),
            )
        if diagnostics:
            temporary_artifacts += (
                ArtifactDescriptor(
                    artifact_id=f'{manifest_id}-DIAG',
                    artifact_type='diagnostic_snapshot',
                    logical_name='diagnostics_json',
                    media_type='application/json',
                    relative_path='diagnostics.json',
                    record_count=len(diagnostics),
                ),
            )
        manifest = self.build_manifest(
            manifest_id=manifest_id,
            intent=intent,
            review_mode=bundle.review_mode,
            artifacts=temporary_artifacts,
            omission_notes=omission_notes,
            warnings=warnings,
        )
        serialized_artifacts = self.serialize_bundle_payloads(
            manifest=manifest,
            bundle=bundle,
            review_artifact=review_artifact,
            profile_snapshots=profile_snapshots,
            diagnostics=diagnostics,
        )
        manifest = self.build_manifest(
            manifest_id=manifest_id,
            intent=intent,
            review_mode=bundle.review_mode,
            artifacts=tuple(item.descriptor for item in serialized_artifacts),
            omission_notes=omission_notes,
            warnings=warnings,
        )
        serialized_artifacts = self.serialize_bundle_payloads(
            manifest=manifest,
            bundle=bundle,
            review_artifact=review_artifact,
            profile_snapshots=profile_snapshots,
            diagnostics=diagnostics,
        )
        result = BundleBuildResult(
            export_intent=intent,
            bundle=bundle,
            manifest=manifest,
            review_artifact=review_artifact,
            serialized_artifacts=serialized_artifacts,
            warnings=warnings,
        )
        self.bundles.append(bundle)
        self.manifests.append(manifest)
        self.export_results.append(result)
        return result

    def build_bundle(
        self,
        *,
        bundle_id: str,
        review_mode: GraphMode,
        command_traces: tuple[CommandTrace, ...] = (),
        restore_results: tuple[RestoreResult, ...] = (),
        alarm_lifecycles: tuple[AlarmLifecycle, ...] = (),
        session_records: tuple[EvidenceRecord, ...] = (),
        overlays: tuple[str, ...] = (),
    ) -> EvidenceBundle:
        intent = self.build_export_intent(
            export_id=bundle_id,
            artifact_class=ExportArtifactClass.EVIDENCE_BUNDLE,
            requested_by_actor=ActorId('system'),
            session_id='session-unknown',
            requested_at=0,
            authority_state=AuthorizationState.ALLOWED,
            scope=self.resolve_export_scope(graph_mode=review_mode, overlays=overlays),
            origin='service-wrapper',
        )
        result = self.build_bundle_from_intent(
            intent=intent,
            bundle_id=bundle_id,
            manifest_id=f'{bundle_id}-MANIFEST',
            command_traces=command_traces,
            restore_results=restore_results,
            alarm_lifecycles=alarm_lifecycles,
            session_records=session_records,
            overlays=overlays,
        )
        return result.bundle
