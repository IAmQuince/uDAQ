from __future__ import annotations

from dataclasses import replace

from universaldaq.app import MappingApplyMode
from universaldaq.common import as_event_time
from universaldaq.mapping import MappingSandboxController, MappingSandboxStateStore, build_demo_apply_request, build_demo_sandbox_state


def test_sandbox_apply_mutates_only_the_sandbox_store() -> None:
    original_state = build_demo_sandbox_state()
    original_hash = original_state.state_hash()
    store = MappingSandboxStateStore(state=original_state)
    request = build_demo_apply_request()

    result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=request,
        created_timestamp=as_event_time(5030),
    )

    assert result.accepted is True
    assert result.before_hash == original_hash
    assert result.after_hash == store.state.state_hash()
    assert result.after_hash != original_hash
    assert original_state.state_hash() == original_hash
    assert result.executed_live is False
    assert result.audit_event is not None
    assert result.audit_event.executed_live is False


def test_sandbox_apply_rejects_execute_live_requests() -> None:
    store = MappingSandboxStateStore(state=build_demo_sandbox_state())
    live_request = replace(build_demo_apply_request(), mode=MappingApplyMode.EXECUTE_LIVE)

    result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=live_request,
        created_timestamp=as_event_time(5040),
    )

    assert result.accepted is False
    assert result.executed_live is False
    assert result.before_hash == result.after_hash
    assert 'only prepared_only and dry_run' in result.blocked_reason
