from __future__ import annotations

from universaldaq.common import as_event_time
from universaldaq.mapping import (
    MappingSandboxController,
    MappingSandboxStateStore,
    build_demo_apply_request,
    build_demo_sandbox_state,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-MAPPING-SANDBOX-004',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-QUAL-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'sandbox rollback restores original state hash without live execution',
}


def test_sandbox_rollback_restores_original_hash() -> None:
    state = build_demo_sandbox_state()
    original_hash = state.state_hash()
    store = MappingSandboxStateStore(state=state)

    apply_result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=build_demo_apply_request(),
        created_timestamp=as_event_time(5050),
    )
    assert apply_result.accepted is True
    assert apply_result.after_hash != original_hash
    assert apply_result.rollback_token is not None

    rollback = store.rollback(rollback_token=apply_result.rollback_token, timestamp=as_event_time(5060))

    assert rollback.accepted is True
    assert store.state.state_hash() == original_hash
    assert rollback.after_hash == original_hash
    assert rollback.executed_live is False


def test_unknown_rollback_token_is_non_mutating_rejection() -> None:
    state = build_demo_sandbox_state()
    store = MappingSandboxStateStore(state=state)
    before_hash = store.state.state_hash()

    rollback = store.rollback(rollback_token='missing-token', timestamp=as_event_time(5070))

    assert rollback.accepted is False
    assert rollback.before_hash == before_hash
    assert rollback.after_hash == before_hash
    assert store.state.state_hash() == before_hash
