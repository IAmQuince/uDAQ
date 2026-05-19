from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_fault_injection import simulate_corrupted_latest_checkpoint

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-032',
    'verifies_requirements': ['UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'fault-injection recovery stress proves fallback from a deeper checkpoint ladder with a non-trivial multi-type replay tail and state-hash validity',
}
pytestmark = pytest.mark.integration


def test_fault_injection_recovery_stress_proves_deeper_fallback(tmp_path):
    report = simulate_corrupted_latest_checkpoint(package_root=PACKAGE_ROOT, output_root=tmp_path / 'fault')
    assert report['verdict'] == 'PASS'
    assert report['fallback_candidate_count'] >= 3
    assert report['replay_tail_count'] >= 16
    assert report['replay_tail_record_type_count'] >= 3
    assert report['replay_tail_contains_multiple_record_types'] is True
    assert report['state_hash_matches'] is True
    detail = json.loads((tmp_path / 'fault' / 'fallback_recovery_detail.json').read_text(encoding='utf-8'))
    assert detail['verdict'] == 'PASS'
    assert (tmp_path / 'fault' / 'session_timeline.md').exists()
