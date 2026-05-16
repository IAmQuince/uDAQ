from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT
from universaldaq.runtime import build_authoritative_runtime_snapshot
from universaldaq.session import DurableSessionService

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-SESSION-001',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'session replay remains non-live, non-mutating, and free of optional hardware support-pack imports',
}
pytestmark = pytest.mark.invariants


def test_replay_view_is_never_live_or_write_authoritative() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-REPLAY-BOUNDARY-001', created_at=600)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id='CHK-REPLAY-BOUNDARY-001',
        timestamp=601,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=601),
    )
    replay = service.build_replay_view(
        session=session,
        checkpoint=checkpoint,
        replay_id='REPLAY-BOUNDARY-001',
        created_at=602,
    )
    payload = replay.to_dict()

    assert payload['replay_is_live'] is False
    assert payload['safety']['hardware_mutation_enabled'] is False
    assert payload['safety']['live_mapping_apply_enabled'] is False
    assert payload['safety']['production_historian_enabled'] is False


def test_session_package_does_not_import_hardware_support_packs_or_write_paths() -> None:
    failures: list[str] = []
    forbidden = (
        'universaldaq_labjack',
        'universaldaq_arduino',
        'universaldaq_rpi',
        'AdapterCommandRequest',
        'request_write',
        'apply_to_sandbox',
    )
    for path in sorted((PACKAGE_ROOT / 'src' / 'universaldaq' / 'session').rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        if any(token in text for token in forbidden):
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
    assert not failures, failures
