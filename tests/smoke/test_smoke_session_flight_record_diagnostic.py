from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-012',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'trusted-session flight-record diagnostic snapshot with provenance, action-audit, and alarm summary',
}


def test_session_flight_record_diagnostic_runs_and_emits_control_and_alarm_posture():
    package_root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_session_flight_record'],
        cwd=package_root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload['trusted_session_inventory']['control_mode_label'] == 'armed_control'
    assert payload['first_signal_replay_tape']['provenance_label']
    assert payload['trusted_session_inventory']['signal_provenance']['channel_metadata']['source_point_id'] == 'demo_wave_0'
