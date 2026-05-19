from __future__ import annotations

from pathlib import Path

from universaldaq.testing import export_diagnostic_bundle, run_sprint_acceptance_suite

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-MAPPING-SANDBOX-005',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-QUAL-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'sprint acceptance harness and diagnostic bundle export both complete without hardware',
}


def test_sprint_acceptance_harness_writes_reports() -> None:
    result = run_sprint_acceptance_suite(package_root=Path.cwd())

    assert result.passed is True
    assert Path(result.report_path).is_file()


def test_diagnostic_bundle_export_writes_zip() -> None:
    result = export_diagnostic_bundle(package_root=Path.cwd())

    assert result.passed is True
    assert result.report_path.endswith('.zip')
    assert Path(result.report_path).is_file()
