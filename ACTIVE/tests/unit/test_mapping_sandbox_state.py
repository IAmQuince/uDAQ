from __future__ import annotations

from universaldaq.common import as_event_time
from universaldaq.mapping import MappingSandboxStateStore, build_demo_sandbox_state


def test_mapping_sandbox_state_hash_is_stable_for_same_payload() -> None:
    state_a = build_demo_sandbox_state()
    state_b = build_demo_sandbox_state()

    assert state_a.state_hash() == state_b.state_hash()
    assert state_a.binding_by_logical_id()['SIG-DEMO-TEMP'].endpoint == 'ANALOG_IN_0'


def test_mapping_sandbox_store_snapshot_does_not_mutate_state() -> None:
    state = build_demo_sandbox_state()
    store = MappingSandboxStateStore(state=state)
    before_hash = store.state.state_hash()

    snapshot = store.snapshot(timestamp=as_event_time(5000), rollback_token='token-1')

    assert snapshot.state_hash == before_hash
    assert store.state.state_hash() == before_hash
    assert store.events[-1].event_kind == 'snapshot_created'
