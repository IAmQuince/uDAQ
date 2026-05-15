from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-020',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001', 'UDQ-REQ-SIG-001'],
    'checks_invariants': ['UDQ-INV-TIME-001', 'UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'bounded U6 diagnostic and live-value smoke scripts run in simulated mode and produce proof files',
}
pytestmark = pytest.mark.integration


def test_u6_diag_script_writes_text_report(tmp_path):
    out_path = tmp_path / 'U6_DIAG.txt'
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'tools.dev.run_u6_diag',
            '--package-root',
            str(PACKAGE_ROOT),
            '--out',
            str(out_path),
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    text = out_path.read_text(encoding='utf-8')
    assert 'UDQ U6 Diagnostic' in text
    assert 'variable_count: 4' in text
    assert 'Runtime Status' in text


def test_u6_live_value_smoke_script_writes_summary_and_journal(tmp_path):
    summary_path = tmp_path / 'U6_LIVE_SUMMARY.txt'
    journal_path = tmp_path / 'U6_LIVE_JOURNAL.jsonl'
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'tools.dev.run_u6_live_value_smoke',
            '--package-root',
            str(PACKAGE_ROOT),
            '--summary',
            str(summary_path),
            '--journal',
            str(journal_path),
            '--cycles',
            '6',
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    summary_text = summary_path.read_text(encoding='utf-8')
    journal_text = journal_path.read_text(encoding='utf-8')
    assert 'UDQ U6 Live Value Smoke' in summary_text
    assert 'avg_abc' in summary_text
    assert 'variable_update' in journal_text
