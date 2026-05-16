from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT
from tests.session_contract_support import (
    append_checkpoint,
    build_replay_from_checkpoint,
    create_checkpoint,
    create_session,
    to_dict,
)
from universaldaq.runtime import build_authoritative_runtime_snapshot

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-SESSION-HELPER-001',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'session replay remains non-live, non-mutating, and free of optional hardware support-pack imports',
}
pytestmark = pytest.mark.invariants


def test_replay_view_is_never_live_or_write_authoritative() -> None:
    session = create_session(session_id='SES-REPLAY-BOUNDARY-001', created_at=600)
    checkpoint = create_checkpoint(
        session=session,
        checkpoint_id='CHK-REPLAY-BOUNDARY-001',
        timestamp=601,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=601),
    )
    session = append_checkpoint(session=session, checkpoint=checkpoint)
    replay = build_replay_from_checkpoint(
        session=session,
        checkpoint=checkpoint,
        replay_id='REPLAY-BOUNDARY-001',
        created_at=602,
    )
    payload = to_dict(replay)

    assert payload['replay_is_live'] is False
    assert payload['safety']['hardware_mutation_enabled'] is False
    assert payload['safety']['live_mapping_apply_enabled'] is False
    assert payload['safety']['production_historian_enabled'] is False
    assert payload['runtime_snapshot']['observed_state']['truth_kind'] == 'observed'


def test_session_package_does_not_import_hardware_support_packs_or_write_paths() -> None:
    session_root = PACKAGE_ROOT / 'src' / 'universaldaq' / 'session'
    if not session_root.exists():
        pytest.skip('pending durable session package merge from GPT-5.5')

    failures: list[str] = []
    forbidden = (
        'universaldaq_labjack',
        'universaldaq_arduino',
        'universaldaq_rpi',
        'AdapterCommandRequest',
        'request_write',
        'apply_to_sandbox',
    )
    for path in sorted(session_root.rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        if any(token in text for token in forbidden):
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
    assert not failures, failures
