from __future__ import annotations

import pytest

from universaldaq.runtime import build_runtime_semantic_state, build_runtime_vocabulary_map, state_family_for

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-097',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime evidence semantics maps layered state tokens into one reviewer-facing family without flattening the source layers',
}
pytestmark = pytest.mark.contract


def test_state_family_mapping_recognizes_layer_specific_tokens():
    assert state_family_for('ready_to_configure') == 'configuration_pre_run'
    assert state_family_for('ready') == 'live_ready_healthy'
    assert state_family_for('live') == 'live_ready_healthy'
    assert state_family_for('disconnected') == 'disconnected'


def test_runtime_vocabulary_map_keeps_layers_and_exposes_alignment():
    vocabulary = build_runtime_vocabulary_map(
        ui_phase='live',
        lifecycle_summary_phase='live',
        adapter_status={'lifecycle_state': 'ready'},
    )
    assert vocabulary['canonical_state']['canonical_state_family'] == 'live_ready_healthy'
    assert vocabulary['canonical_state']['reviewer_label'] == 'live / ready / healthy'
    assert vocabulary['alignment']['ui_family_matches_lifecycle_family'] is True
    assert vocabulary['alignment']['adapter_family_matches_lifecycle_family'] is True


def test_runtime_semantic_state_prefers_lifecycle_summary_phase_for_reviewer_rollup():
    semantic_state = build_runtime_semantic_state(
        ui_phase='live',
        lifecycle_summary_phase='disconnected',
        adapter_status={'lifecycle_state': 'ready'},
    )
    assert semantic_state.authoritative_layer == 'lifecycle_summary_phase'
    assert semantic_state.canonical_state_family == 'disconnected'
    assert semantic_state.reviewer_label == 'disconnected'



def test_runtime_semantic_state_prefers_adapter_incident_over_configuration_language():
    semantic_state = build_runtime_semantic_state(
        ui_phase='live',
        lifecycle_summary_phase='ready_to_configure',
        adapter_status={'lifecycle_state': 'degraded'},
    )
    assert semantic_state.authoritative_layer == 'adapter_lifecycle_state'
    assert semantic_state.canonical_state_family == 'degraded'
    assert semantic_state.reviewer_label == 'degraded'
