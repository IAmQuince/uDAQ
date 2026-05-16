from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT
from tests.runtime_state_contract_support import (
    build_degraded_runtime_state_payload,
    materialize_runtime_state_snapshot,
    runtime_state_to_dict,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-019',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-ARCH-002'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime-state boundary checks keep vendor imports out of runtime modules and preserve sandbox-only mapping posture when the authoritative snapshot API lands',
}
pytestmark = pytest.mark.invariants


def test_runtime_package_imports_without_optional_vendor_support_packs() -> None:
    import universaldaq.runtime as runtime_module

    assert runtime_module is not None
    assert hasattr(runtime_module, 'RuntimeQualityService')


def test_runtime_modules_do_not_import_optional_vendor_support_packs() -> None:
    failures: list[str] = []
    forbidden = ('universaldaq_labjack', 'universaldaq_arduino', 'universaldaq_rpi', 'labjack')
    for path in sorted((PACKAGE_ROOT / 'src' / 'universaldaq' / 'runtime').rglob('*.py')):
        text = path.read_text(encoding='utf-8').lower()
        if any(marker in text for marker in forbidden):
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
    assert not failures, failures


def test_authoritative_runtime_snapshot_contract_keeps_sandbox_mappings_non_authoritative() -> None:
    snapshot = materialize_runtime_state_snapshot(build_degraded_runtime_state_payload())
    payload = runtime_state_to_dict(snapshot)

    assert payload['mappings']['drafts'][0]['posture'] == 'sandbox-only'
    assert payload['mappings']['drafts'][0]['authoritative_applied'] is False
    assert payload['mappings']['applied'][0]['authoritative_applied'] is True
    assert payload['command_posture']['hardware_write_authorized'] is False
