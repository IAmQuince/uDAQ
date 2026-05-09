from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_real_hardware_specimen_bridge import run_real_hardware_specimen_bridge

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-036',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-007'],
    'checks_invariants': ['UDQ-INV-EVID-006', 'UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'bounded real-hardware specimen bridge keeps the acceptance surface flat, skips honestly when hardware is unavailable, and emits reviewable artifacts when a real-mode backend is available',
}
pytestmark = pytest.mark.integration


class _FakeU6:
    serialNumber = 470001
    firmwareVersion = '1.15'
    hardwareVersion = '2.0'

    def __init__(self, values: tuple[float, float, float] = (1.25, 2.5, 3.75)) -> None:
        self.values = values

    def getCalibrationData(self) -> None:
        return None

    def getAIN(self, channel: int) -> float:
        return self.values[channel]

    def close(self) -> None:
        return None



def test_real_hardware_specimen_bridge_skips_cleanly_when_driver_unavailable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr('universaldaq_labjack.discovery.probe_driver_status', lambda: (False, 'not-installed'))

    report = run_real_hardware_specimen_bridge(
        package_root=PACKAGE_ROOT,
        output_root=tmp_path / 'real_bridge',
    )

    assert report['verdict'] == 'SKIP'
    assert report['mode'] == 'driver_unavailable'
    assert (tmp_path / 'real_bridge' / 'real_hardware_bridge_report.json').exists()
    assert (tmp_path / 'real_bridge' / 'real_hardware_bridge_report.md').exists()



def test_real_hardware_specimen_bridge_emits_reviewable_artifacts_with_injected_backend(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr('universaldaq_labjack.discovery.probe_driver_status', lambda: (True, 'injected-backend'))

    report = run_real_hardware_specimen_bridge(
        package_root=PACKAGE_ROOT,
        output_root=tmp_path / 'real_bridge',
        real_backend_factory=lambda serial_number: _FakeU6(),
    )

    assert report['verdict'] == 'PASS'
    assert report['history_tier_summary']['hot']['recent_sample_count'] > 0
    assert report['history_tier_summary']['warm']['variable_row_count'] > 0
    assert report['checkpoint_summary']['valid_checkpoint_count'] >= 1
    assert bool(report['history_index_report']['sample_counts_by_point'])
    assert (tmp_path / 'real_bridge' / 'review_summary.json').exists()
    assert (tmp_path / 'real_bridge' / 'review_summary.md').exists()
