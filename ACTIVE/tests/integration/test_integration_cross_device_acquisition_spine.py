from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_cross_device_acquisition_spine import run_cross_device_acquisition_spine

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-037',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DEV-001', 'UDQ-REQ-SIG-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-004', 'UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'cross-device acquisition spine keeps the proven evidence lane intact while normalizing simultaneous multi-adapter ingest into canonical tags and mixed-source review artifacts',
}
pytestmark = pytest.mark.integration


def test_cross_device_acquisition_spine_emits_pass_report(tmp_path: Path):
    report = run_cross_device_acquisition_spine(package_root=PACKAGE_ROOT, output_root=tmp_path / 'cross_device')

    assert report['verdict'] == 'PASS'
    assert report['activated_adapter_count'] >= 3
    assert report['tag_definition_count'] >= 10
    assert report['latest_sample_count'] >= 10
    assert len(report['history_index_report']['sample_counts_by_point']) >= 6
    assert len(report['history_index_report']['variable_ids']) >= 3
    report_dir = Path(report['report_dir'])
    json_report = json.loads((report_dir / 'cross_device_acquisition_report.json').read_text(encoding='utf-8'))
    assert json_report['verdict'] == 'PASS'
    assert (report_dir / 'cross_device_acquisition_report.md').exists()
    assert (report_dir / 'tag_inventory.json').exists()
    assert (report_dir / 'tag_inventory.md').exists()
    assert (report_dir / 'review_summary.json').exists()
