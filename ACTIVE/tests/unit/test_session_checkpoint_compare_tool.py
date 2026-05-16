from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-DIAG-SESSION-CHECKPOINT-002',
    'verifies_requirements': ['UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'session checkpoint compare report highlights changed fields safely',
}


def test_compare_session_checkpoints_reports_changed_fields(tmp_path: Path) -> None:
    left = {
        'session_model_version': 'udq.session.v1',
        'session_id': 'S-1',
        'checkpoint_id': 'C-1',
        'checkpoint_timestamp': '2026-05-16T00:00:00Z',
        'runtime_snapshot_id': 'R-1',
        'runtime_state_model_version': 'udq.runtime.state.v1',
        'checkpoint_count': 1,
        'event_count': 2,
        'warning_count': 0,
        'degraded_count': 0,
        'stale_count': 0,
        'unavailable_count': 0,
        'session_api_available': False,
        'replay_is_live': False,
        'hardware_mutation_enabled': False,
        'live_mapping_apply_enabled': False,
    }
    right = dict(left)
    right['checkpoint_id'] = 'C-2'
    right['event_count'] = 7

    left_path = tmp_path / 'left.json'
    right_path = tmp_path / 'right.json'
    left_path.write_text(json.dumps(left), encoding='utf-8')
    right_path.write_text(json.dumps(right), encoding='utf-8')

    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'tools.diagnostics.compare_session_checkpoints',
            '--left',
            str(left_path),
            '--right',
            str(right_path),
            '--pretty',
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['changed_field_count'] == 2
    changed_fields = {item['field'] for item in payload['fields_changed']}
    assert changed_fields == {'checkpoint_id', 'event_count'}
