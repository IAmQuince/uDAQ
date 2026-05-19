from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-026',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-GOV-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'guided U6 field-validation evidence bundle in simulated mode',
}
pytestmark = pytest.mark.integration


def test_u6_field_test_harness_writes_guided_bundle_files(tmp_path):
    output_dir = tmp_path / 'field_tests'
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'tools.dev.run_u6_field_test_harness',
            '--package-root',
            str(PACKAGE_ROOT),
            '--output-dir',
            str(output_dir),
            '--noninteractive',
            '--baseline-cycles',
            '2',
            '--loss-cycles',
            '2',
            '--recovery-cycles',
            '2',
            '--stabilization-cycles',
            '2',
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    bundle_dirs = [path for path in output_dir.iterdir() if path.is_dir()]
    assert len(bundle_dirs) == 1
    bundle_dir = bundle_dirs[0]
    diagnostics_files = list(bundle_dir.glob('*__diagnostics.json'))
    summary_files = list(bundle_dir.glob('*__summary.txt'))
    events_files = list(bundle_dir.glob('*__events.csv'))
    smoke_files = list(bundle_dir.glob('*__smoke.txt'))
    preflight_files = list(bundle_dir.glob('*__preflight-report.json'))
    verdict_files = list(bundle_dir.glob('*__semantic-consistency-verdict.json'))
    manifest_files = list(bundle_dir.glob('*__artifact-manifest.json'))
    start_here_files = list(bundle_dir.glob('*__start-here.txt'))
    review_summary_files = list(bundle_dir.glob('*__review-summary.md'))
    assert diagnostics_files and summary_files and events_files and smoke_files
    assert preflight_files and verdict_files and manifest_files
    assert start_here_files and review_summary_files
    start_here = start_here_files[0]

    payload = json.loads(diagnostics_files[0].read_text(encoding='utf-8'))
    assert payload['session_metadata']['requested_mode'] == 'simulated'
    assert payload['session_metadata']['validation_flow'] == 'guided_unplug_replug_validation'
    assert len(payload['session_metadata']['discovered_devices']) >= 1
    assert len(payload['captures']) == 4
    assert payload['captures'][0]['adapter_status']['hardware_mode'] == 'simulated'
    assert 'incident_summary' in payload
    assert 'phase_records' in payload
    assert payload['semantic_consistency']['verdict'] == 'PASS'
    assert payload['phase_records'][-1]['phase_name'] == 'post_recovery_stabilization'

    summary_text = summary_files[0].read_text(encoding='utf-8')
    assert 'Phase Timeline' in summary_text
    assert 'Semantic Consistency Checks' in summary_text
    assert 'Reviewer Runtime Rollup' in summary_text

    start_here_text = start_here.read_text(encoding='utf-8')
    assert 'Semantic verdict: PASS' in start_here_text
    manifest_payload = json.loads(manifest_files[0].read_text(encoding='utf-8'))
    labels = {row['label'] for row in manifest_payload['artifacts']}
    assert 'diagnostics' in labels
    assert 'semantic_verdict_json' in labels


def test_u6_field_test_harness_supports_startup_smoke_only(tmp_path):
    output_dir = tmp_path / 'field_tests_smoke'
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'tools.dev.run_u6_field_test_harness',
            '--package-root',
            str(PACKAGE_ROOT),
            '--output-dir',
            str(output_dir),
            '--startup-smoke-only',
            '--noninteractive',
            '--baseline-cycles',
            '2',
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    bundle_dir = next(path for path in output_dir.iterdir() if path.is_dir())
    diagnostics_path = next(bundle_dir.glob('*__diagnostics.json'))
    payload = json.loads(diagnostics_path.read_text(encoding='utf-8'))
    assert payload['session_metadata']['validation_flow'] == 'startup_open_smoke'
    assert len(payload['captures']) == 1
    assert payload['phase_records'][0]['phase_name'] == 'baseline'
