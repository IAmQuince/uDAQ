from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


STATE_FAMILY_LABELS = {
    'configuration_pre_run': 'pre-run / configure',
    'initializing': 'initializing',
    'live_ready_healthy': 'live / ready / healthy',
    'degraded': 'degraded',
    'disconnected': 'disconnected',
    'recovering': 'recovering',
    'faulted': 'faulted',
    'shutting_down': 'shutting down',
    'stopped': 'stopped',
    'unknown': 'unknown',
}

_STATE_FAMILY_MAP = {
    'configured': 'configuration_pre_run',
    'configuration': 'configuration_pre_run',
    'configuring': 'configuration_pre_run',
    'ready_to_configure': 'configuration_pre_run',
    'discovered': 'configuration_pre_run',
    'no_device': 'configuration_pre_run',
    'initializing': 'initializing',
    'startup': 'initializing',
    'starting': 'initializing',
    'ready': 'live_ready_healthy',
    'live': 'live_ready_healthy',
    'healthy': 'live_ready_healthy',
    'connected': 'live_ready_healthy',
    'degraded': 'degraded',
    'disconnected': 'disconnected',
    'recovering': 'recovering',
    'faulted': 'faulted',
    'failed': 'faulted',
    'shutting_down': 'shutting_down',
    'stopping': 'shutting_down',
    'stopped': 'stopped',
    'unknown': 'unknown',
}

_VOCABULARY_LAYER_RULES = (
    {
        'layer': 'ui_phase',
        'authority_scope': 'shell-facing posture and operator review surface',
        'canonical_when': 'the shell is rendering current session posture',
        'notes': 'This layer should stay readable for operators and reviewers and does not need to expose support-pack implementation detail.',
    },
    {
        'layer': 'lifecycle_summary_phase',
        'authority_scope': 'bounded lifecycle review summary',
        'canonical_when': 'a reviewer needs the current runtime posture for the active bounded slice',
        'notes': 'This layer is the preferred human-facing runtime state for lifecycle review bundles.',
    },
    {
        'layer': 'adapter_lifecycle_state',
        'authority_scope': 'device/support-pack runtime condition',
        'canonical_when': 'device-specific condition is needed to explain degradation, disconnects, or recovery stages',
        'notes': 'This layer may use provider-specific states such as ready or degraded while still mapping cleanly into platform families.',
    },
    {
        'layer': 'state_family',
        'authority_scope': 'cross-layer semantic reconciliation',
        'canonical_when': 'multiple layers must be compared without implying contradiction',
        'notes': 'This layer intentionally normalizes families, not every concrete state token.',
    },
    {
        'layer': 'reviewer_label',
        'authority_scope': 'PM/reviewer rollup language',
        'canonical_when': 'a package needs one concise runtime phrase that remains traceable back to runtime and adapter truth',
        'notes': 'This layer is derived and must never override deeper technical evidence.',
    },
)

_TAXONOMY_CATEGORY_RULES = {
    'runtime_event': {
        'meaning': 'meaningful runtime-observed transition or state change',
        'appears_in_summary': True,
        'appears_in_csv_json': True,
        'pm_rollup_visible': True,
        'audience': 'reviewer_and_engineering',
    },
    'alarm_event': {
        'meaning': 'alarm lifecycle transition or active alarm status surface',
        'appears_in_summary': True,
        'appears_in_csv_json': True,
        'pm_rollup_visible': True,
        'audience': 'reviewer_and_engineering',
    },
    'operator_action': {
        'meaning': 'human or commanded action admitted through the governed shell path',
        'appears_in_summary': True,
        'appears_in_csv_json': True,
        'pm_rollup_visible': True,
        'audience': 'reviewer_and_engineering',
    },
    'automation_claim': {
        'meaning': 'bounded automation claim, suppression, or resolution record',
        'appears_in_summary': False,
        'appears_in_csv_json': True,
        'pm_rollup_visible': False,
        'audience': 'engineering',
    },
    'diagnostic_snapshot': {
        'meaning': 'snapshot/counter/buffer/journal evidence describing runtime condition without claiming a discrete event',
        'appears_in_summary': False,
        'appears_in_csv_json': True,
        'pm_rollup_visible': False,
        'audience': 'engineering',
    },
}


@dataclass(frozen=True, slots=True)
class RuntimeSemanticState:
    ui_phase: str | None
    lifecycle_summary_phase: str | None
    adapter_lifecycle_state: str | None
    canonical_state_family: str
    reviewer_label: str
    authoritative_layer: str

    def as_dict(self) -> dict[str, object]:
        return {
            'ui_phase': self.ui_phase,
            'lifecycle_summary_phase': self.lifecycle_summary_phase,
            'adapter_lifecycle_state': self.adapter_lifecycle_state,
            'canonical_state_family': self.canonical_state_family,
            'reviewer_label': self.reviewer_label,
            'authoritative_layer': self.authoritative_layer,
        }


@dataclass(frozen=True, slots=True)
class RuntimeAudienceMetricLayers:
    reviewer_metrics: dict[str, object]
    engineering_metrics: dict[str, object]
    internal_metrics: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            'reviewer_metrics': self.reviewer_metrics,
            'engineering_metrics': self.engineering_metrics,
            'internal_metrics': self.internal_metrics,
        }


def _normalized_text(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    return text or None


def state_family_for(value: object | None) -> str:
    normalized = _normalized_text(value)
    if normalized is None:
        return 'unknown'
    return _STATE_FAMILY_MAP.get(normalized, 'unknown')


def reviewer_label_for_family(state_family: str) -> str:
    return STATE_FAMILY_LABELS.get(state_family, STATE_FAMILY_LABELS['unknown'])


def _authoritative_layer(*, lifecycle_summary_phase: str | None, ui_phase: str | None, adapter_lifecycle_state: str | None) -> str:
    if lifecycle_summary_phase:
        return 'lifecycle_summary_phase'
    if ui_phase:
        return 'ui_phase'
    if adapter_lifecycle_state:
        return 'adapter_lifecycle_state'
    return 'state_family'


def build_runtime_semantic_state(
    *,
    ui_phase: object | None,
    lifecycle_summary_phase: object | None,
    adapter_status: Mapping[str, object] | None,
) -> RuntimeSemanticState:
    ui_phase_text = None if ui_phase is None else str(ui_phase)
    lifecycle_phase_text = None if lifecycle_summary_phase is None else str(lifecycle_summary_phase)
    adapter_lifecycle_state = None if adapter_status is None else (None if adapter_status.get('lifecycle_state') is None else str(adapter_status.get('lifecycle_state')))
    ui_family = state_family_for(ui_phase_text)
    lifecycle_family = state_family_for(lifecycle_phase_text)
    adapter_family = state_family_for(adapter_lifecycle_state)
    authoritative_layer = _authoritative_layer(
        lifecycle_summary_phase=lifecycle_phase_text,
        ui_phase=ui_phase_text,
        adapter_lifecycle_state=adapter_lifecycle_state,
    )
    if lifecycle_family == 'configuration_pre_run' and adapter_family in {'degraded', 'disconnected', 'recovering', 'faulted'}:
        authoritative_layer = 'adapter_lifecycle_state'
    authoritative_value = {
        'lifecycle_summary_phase': lifecycle_phase_text,
        'ui_phase': ui_phase_text,
        'adapter_lifecycle_state': adapter_lifecycle_state,
        'state_family': None,
    }.get(authoritative_layer)
    canonical_state_family = state_family_for(authoritative_value)
    if canonical_state_family == 'unknown':
        canonical_state_family = state_family_for(adapter_lifecycle_state)
    if canonical_state_family == 'unknown':
        canonical_state_family = state_family_for(ui_phase_text)
    if canonical_state_family == 'unknown':
        canonical_state_family = state_family_for(lifecycle_phase_text)
    reviewer_label = reviewer_label_for_family(canonical_state_family)
    return RuntimeSemanticState(
        ui_phase=ui_phase_text,
        lifecycle_summary_phase=lifecycle_phase_text,
        adapter_lifecycle_state=adapter_lifecycle_state,
        canonical_state_family=canonical_state_family,
        reviewer_label=reviewer_label,
        authoritative_layer=authoritative_layer,
    )


def build_runtime_vocabulary_map(
    *,
    ui_phase: object | None,
    lifecycle_summary_phase: object | None,
    adapter_status: Mapping[str, object] | None,
) -> dict[str, object]:
    semantic_state = build_runtime_semantic_state(
        ui_phase=ui_phase,
        lifecycle_summary_phase=lifecycle_summary_phase,
        adapter_status=adapter_status,
    )
    ui_family = state_family_for(semantic_state.ui_phase)
    lifecycle_family = state_family_for(semantic_state.lifecycle_summary_phase)
    adapter_family = state_family_for(semantic_state.adapter_lifecycle_state)
    return {
        'bundle_version': 'v1',
        'layer_rules': deepcopy(_VOCABULARY_LAYER_RULES),
        'state_family_labels': dict(STATE_FAMILY_LABELS),
        'state_family_map': dict(sorted(_STATE_FAMILY_MAP.items())),
        'canonical_state': semantic_state.as_dict(),
        'alignment': {
            'ui_matches_lifecycle_phase': semantic_state.ui_phase == semantic_state.lifecycle_summary_phase,
            'ui_family_matches_lifecycle_family': ui_family == lifecycle_family,
            'adapter_family_matches_lifecycle_family': adapter_family == lifecycle_family,
            'adapter_family_matches_ui_family': adapter_family == ui_family,
            'ui_state_family': ui_family,
            'lifecycle_summary_state_family': lifecycle_family,
            'adapter_state_family': adapter_family,
        },
    }


def _taxonomy_meta(category: str) -> dict[str, object]:
    meta = _TAXONOMY_CATEGORY_RULES[category]
    return {'category': category, **meta}


def annotate_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    category: str,
    source_surface: str,
    owner_module: str,
) -> list[dict[str, object]]:
    meta = _taxonomy_meta(category)
    annotated: list[dict[str, object]] = []
    for row in rows:
        payload = {str(key): value for key, value in row.items()}
        payload['coherence'] = {
            'source_surface': source_surface,
            'owner_module': owner_module,
            **meta,
        }
        annotated.append(payload)
    return annotated


def build_runtime_event_taxonomy(
    *,
    recent_runtime_event_rows: Sequence[Mapping[str, object]],
    recent_event_rows: Sequence[Mapping[str, object]],
    recent_command_rows: Sequence[Mapping[str, object]],
    recent_action_claim_rows: Sequence[Mapping[str, object]],
    runtime_variable_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    return {
        'bundle_version': 'v1',
        'category_rules': deepcopy(_TAXONOMY_CATEGORY_RULES),
        'recent_runtime_events': annotate_rows(
            recent_runtime_event_rows,
            category='runtime_event',
            source_surface='recent_runtime_event_rows',
            owner_module='src/universaldaq/runtime/services.py',
        ),
        'recent_alarm_events': annotate_rows(
            recent_event_rows,
            category='alarm_event',
            source_surface='recent_event_rows',
            owner_module='src/universaldaq/events/services.py',
        ),
        'recent_operator_actions': annotate_rows(
            recent_command_rows,
            category='operator_action',
            source_surface='recent_command_rows',
            owner_module='src/universaldaq/commands/services.py',
        ),
        'recent_automation_claims': annotate_rows(
            recent_action_claim_rows,
            category='automation_claim',
            source_surface='recent_action_claim_rows',
            owner_module='src/universaldaq/automation/claims.py',
        ),
        'recent_diagnostic_rows': annotate_rows(
            runtime_variable_rows,
            category='diagnostic_snapshot',
            source_surface='runtime_variable_rows',
            owner_module='src/universaldaq/runtime/services.py',
        ),
    }


def build_runtime_truth_surface_inventory() -> list[dict[str, object]]:
    return [
        {
            'surface': 'lifecycle_summary',
            'owner_module': 'src/universaldaq/app/lifecycle_orchestrator.py',
            'audience': 'reviewer_and_engineering',
            'authority': 'derived_review_surface',
            'purpose': 'bounded lifecycle posture for the active shell session',
        },
        {
            'surface': 'active_adapter_status',
            'owner_module': 'src/universaldaq/app/device_lifecycle_handler.py',
            'audience': 'engineering_with_reviewer_support',
            'authority': 'device_support_pack_surface',
            'purpose': 'device/support-pack runtime condition and recovery counters',
        },
        {
            'surface': 'runtime_status',
            'owner_module': 'src/universaldaq/runtime/services.py',
            'audience': 'engineering',
            'authority': 'canonical_runtime_snapshot',
            'purpose': 'bounded queue, journal, and presentation status counters',
        },
        {
            'surface': 'recent_runtime_event_rows',
            'owner_module': 'src/universaldaq/runtime/services.py',
            'audience': 'reviewer_and_engineering',
            'authority': 'runtime_event_surface',
            'purpose': 'meaningful runtime transitions recorded by the bounded runtime spine',
        },
        {
            'surface': 'recent_event_rows',
            'owner_module': 'src/universaldaq/events/services.py',
            'audience': 'reviewer_and_engineering',
            'authority': 'alarm_event_surface',
            'purpose': 'alarm lifecycle transitions and acknowledgments',
        },
        {
            'surface': 'recent_command_rows',
            'owner_module': 'src/universaldaq/commands/services.py',
            'audience': 'reviewer_and_engineering',
            'authority': 'operator_action_surface',
            'purpose': 'governed command/operator actions admitted or rejected by the shell',
        },
        {
            'surface': 'recent_action_claim_rows',
            'owner_module': 'src/universaldaq/automation/claims.py',
            'audience': 'engineering',
            'authority': 'automation_claim_surface',
            'purpose': 'bounded automation claim/suppression continuity',
        },
        {
            'surface': 'runtime_performance',
            'owner_module': 'src/universaldaq/common/metrics.py',
            'audience': 'engineering',
            'authority': 'runtime_metrics_snapshot',
            'purpose': 'timings, counters, and gauges used for diagnostics and proof',
        },
        {
            'surface': 'reviewer_runtime_rollup',
            'owner_module': 'src/universaldaq/app/automation_review_handler.py',
            'audience': 'reviewer',
            'authority': 'derived_rollup',
            'purpose': 'reviewer-facing statement rendered from canonical runtime evidence',
        },
    ]


def build_runtime_metric_layers(
    *,
    runtime_status: Mapping[str, object],
    event_alarm_summary: Mapping[str, object],
    command_summary: Mapping[str, object],
    runtime_performance: Mapping[str, object],
    adapter_status: Mapping[str, object] | None,
    semantic_state: RuntimeSemanticState,
) -> RuntimeAudienceMetricLayers:
    reviewer_metrics = {
        'reviewer_label': semantic_state.reviewer_label,
        'state_family': semantic_state.canonical_state_family,
        'active_alarm_count': int(event_alarm_summary.get('active_alarm_count', 0) or 0),
        'unacknowledged_alarm_count': int(event_alarm_summary.get('unacknowledged_alarm_count', 0) or 0),
        'highest_active_severity': event_alarm_summary.get('highest_active_severity'),
        'disconnect_count': 0 if adapter_status is None else int(adapter_status.get('disconnect_count', 0) or 0),
        'recovery_count': 0 if adapter_status is None else int(adapter_status.get('recovery_count', 0) or 0),
        'recent_runtime_event_count': int(runtime_status.get('recent_runtime_event_count', 0) or 0),
        'recent_operator_action_count': int(command_summary.get('command_count', 0) or 0),
        'needs_review': bool(event_alarm_summary.get('active_alarm_count', 0) or (0 if adapter_status is None else int(adapter_status.get('consecutive_failures', 0) or 0) > 0)),
    }
    engineering_metrics = {
        'acquisition_queue_depth': int(runtime_status.get('acquisition_queue_depth', 0) or 0),
        'acquisition_queue_dropped': int(runtime_status.get('acquisition_queue_dropped', 0) or 0),
        'presentation_publish_count': int(runtime_status.get('presentation_publish_count', 0) or 0),
        'presentation_coalesced_count': int(runtime_status.get('presentation_coalesced_count', 0) or 0),
        'recent_sample_count': int(runtime_status.get('recent_sample_count', 0) or 0),
        'recent_cycle_count': int(runtime_status.get('recent_cycle_count', 0) or 0),
        'recent_variable_transition_count': int(runtime_status.get('recent_variable_transition_count', 0) or 0),
        'journal_write_count': int(runtime_status.get('journal_write_count', 0) or 0),
        'journal_flush_count': int(runtime_status.get('journal_flush_count', 0) or 0),
        'journal_queue_dropped': int(runtime_status.get('journal_queue_dropped', 0) or 0),
        'adapter_consecutive_failures': 0 if adapter_status is None else int(adapter_status.get('consecutive_failures', 0) or 0),
        'adapter_reconnect_attempts': 0 if adapter_status is None else int(adapter_status.get('reconnect_attempts', 0) or 0),
    }
    counters = runtime_performance.get('counters', {})
    timings = runtime_performance.get('timings', {})
    gauges = runtime_performance.get('gauges', {})
    internal_metrics = {
        'selected_counters': {
            key: counters[key]
            for key in sorted(counters)
            if key.startswith('runtime.') or key.startswith('commands.')
        },
        'selected_timings': {
            key: timings[key]
            for key in sorted(timings)
            if key.startswith('runtime.')
        },
        'selected_gauges': {
            key: gauges[key]
            for key in sorted(gauges)
            if key.startswith('runtime.')
        },
    }
    return RuntimeAudienceMetricLayers(
        reviewer_metrics=reviewer_metrics,
        engineering_metrics=engineering_metrics,
        internal_metrics=internal_metrics,
    )


def build_runtime_reviewer_rollup(
    *,
    semantic_state: RuntimeSemanticState,
    metric_layers: RuntimeAudienceMetricLayers,
    event_taxonomy: Mapping[str, object],
    adapter_status: Mapping[str, object] | None,
) -> dict[str, object]:
    reviewer_metrics = metric_layers.reviewer_metrics
    runtime_events = event_taxonomy.get('recent_runtime_events', [])
    alarm_events = event_taxonomy.get('recent_alarm_events', [])
    operator_actions = event_taxonomy.get('recent_operator_actions', [])
    notable_runtime_types = [
        str(row.get('event_type', row.get('record_type', 'runtime_event')))
        for row in runtime_events[-5:]
    ]
    notable_alarm_types = [
        str(row.get('event_type', row.get('record_type', 'alarm_event')))
        for row in alarm_events[-5:]
    ]
    return {
        'state_family': semantic_state.canonical_state_family,
        'reviewer_label': semantic_state.reviewer_label,
        'summary': (
            f"Runtime posture is {semantic_state.reviewer_label}; "
            f"alarms={reviewer_metrics['active_alarm_count']}, "
            f"disconnects={reviewer_metrics['disconnect_count']}, "
            f"recoveries={reviewer_metrics['recovery_count']}."
        ),
        'active_alarm_count': reviewer_metrics['active_alarm_count'],
        'disconnect_count': reviewer_metrics['disconnect_count'],
        'recovery_count': reviewer_metrics['recovery_count'],
        'active_adapter_id': None if adapter_status is None else adapter_status.get('adapter_id'),
        'adapter_lifecycle_state': None if adapter_status is None else adapter_status.get('lifecycle_state', adapter_status.get('status')),
        'recent_runtime_event_types': notable_runtime_types,
        'recent_alarm_event_types': notable_alarm_types,
        'recent_operator_action_count': len(operator_actions),
    }


def build_canonical_runtime_evidence_bundle(
    *,
    lifecycle_summary: Mapping[str, object],
    binding_review_summary: Mapping[str, object],
    variable_health_summary: Mapping[str, object],
    runtime_status: Mapping[str, object],
    runtime_performance: Mapping[str, object],
    event_alarm_summary: Mapping[str, object],
    command_summary: Mapping[str, object],
    action_claim_summary: Mapping[str, object],
    runtime_vocabulary: Mapping[str, object],
    event_taxonomy: Mapping[str, object],
    metric_layers: RuntimeAudienceMetricLayers,
    reviewer_rollup: Mapping[str, object],
    adapter_status: Mapping[str, object] | None,
    active_adapter_id: str | None,
    active_device_key: str | None,
) -> dict[str, object]:
    return {
        'bundle_version': 'v1',
        'package_surface': 'lifecycle_review_bundle',
        'identity': {
            'active_adapter_id': active_adapter_id,
            'active_device_key': active_device_key,
        },
        'runtime_state': deepcopy(runtime_vocabulary.get('canonical_state', {})),
        'reviewer_rollup': dict(reviewer_rollup),
        'summaries': {
            'lifecycle_summary': dict(lifecycle_summary),
            'binding_review_summary': dict(binding_review_summary),
            'variable_health_summary': dict(variable_health_summary),
            'event_alarm_summary': dict(event_alarm_summary),
            'command_summary': dict(command_summary),
            'action_claim_summary': dict(action_claim_summary),
        },
        'recent_runtime_events': list(event_taxonomy.get('recent_runtime_events', [])),
        'recent_alarm_events': list(event_taxonomy.get('recent_alarm_events', [])),
        'recent_operator_actions': list(event_taxonomy.get('recent_operator_actions', [])),
        'recent_automation_claims': list(event_taxonomy.get('recent_automation_claims', [])),
        'diagnostic_snapshots': {
            'runtime_status': dict(runtime_status),
            'runtime_performance': dict(runtime_performance),
            'active_adapter_status': None if adapter_status is None else dict(adapter_status),
            'recent_diagnostic_rows': list(event_taxonomy.get('recent_diagnostic_rows', [])),
        },
        'metric_layers': metric_layers.as_dict(),
        'provenance': {
            'runtime_truth_surface_inventory': build_runtime_truth_surface_inventory(),
            'vocabulary_alignment': dict(runtime_vocabulary.get('alignment', {})),
        },
    }
