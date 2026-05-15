from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_cross_device_command_arbitration import run_cross_device_command_arbitration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-039',
    'verifies_requirements': ['UDQ-REQ-OUT-001', 'UDQ-REQ-OUT-002', 'UDQ-REQ-ARCH-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'bounded cross-device command arbitration produces canonical writable tags, ownership conflict rejection, degraded target handling, and replayable command evidence without a second harness',
}
pytestmark = pytest.mark.integration


def test_cross_device_command_arbitration_emits_pass_report(tmp_path: Path):
    report = run_cross_device_command_arbitration(package_root=PACKAGE_ROOT, output_root=tmp_path / 'cross_device_commands')

    assert report['verdict'] == 'PASS'
    assert report['writable_tag_count'] >= 3
    assert report['command_summary']['accepted_count'] >= 5
    assert report['command_summary']['ownership_conflict_count'] >= 1
    assert report['command_summary']['same_owner_renewal_count'] >= 1
    assert report['command_summary']['target_unavailable_count'] >= 2
    assert report['degraded_report']['degraded_transition_count'] >= 5
    assert report['degraded_report']['simultaneous_drop_event_count'] >= 1
    assert report['degraded_report']['lease_revoked_on_degrade_count'] >= 1
    assert report['replay_report']['tail_record_count'] >= 4
    assert report['replay_report']['tail_contains_multiple_record_types'] is True

    report_dir = Path(report['report_dir'])
    json_report = json.loads((report_dir / 'cross_device_command_arbitration_report.json').read_text(encoding='utf-8'))
    assert json_report['verdict'] == 'PASS'
    assert (report_dir / 'cross_device_command_arbitration_report.md').exists()
    assert (report_dir / 'writable_tag_inventory.json').exists()
    assert (report_dir / 'command_timeline.json').exists()
    assert (report_dir / 'ownership_ledger.json').exists()
    ownership = json.loads((report_dir / 'ownership_ledger.json').read_text(encoding='utf-8'))
    assert any(row['event_type'] == 'ownership_renewed' for row in ownership['rows'])
    assert any(row['event_type'] == 'lease_revoked_on_degrade' for row in ownership['rows'])
