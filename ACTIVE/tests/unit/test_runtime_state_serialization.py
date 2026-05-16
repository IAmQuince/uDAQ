from __future__ import annotations

from tests.runtime_state_contract_support import (
    build_degraded_runtime_state_payload,
    build_empty_runtime_state_payload,
    canonical_runtime_state_json,
    materialize_runtime_state_snapshot,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-UNIT-003',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'authoritative runtime-state serialization is deterministic and survives unknown/degraded values for diagnostics',
}


def test_runtime_state_serialization_is_deterministic_for_same_payload() -> None:
    first = materialize_runtime_state_snapshot(build_empty_runtime_state_payload())
    second = materialize_runtime_state_snapshot(build_empty_runtime_state_payload())

    assert canonical_runtime_state_json(first) == canonical_runtime_state_json(second)


def test_runtime_state_serialization_survives_unknown_and_degraded_values() -> None:
    snapshot = materialize_runtime_state_snapshot(build_degraded_runtime_state_payload())
    serialized = canonical_runtime_state_json(snapshot)

    assert '"freshness_state":"stale"' in serialized
    assert '"freshness_state":"unknown"' in serialized
    assert '"availability_state":"recovering"' in serialized
    assert '"state":"degraded"' in serialized
