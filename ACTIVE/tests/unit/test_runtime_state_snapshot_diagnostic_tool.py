from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.conftest import PACKAGE_ROOT
from tools.diagnostics import dump_runtime_state_snapshot as snapshot_tool

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-DIAG-RUNTIME-SNAPSHOT-001',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime-state diagnostic artifact remains non-authoritative and hardware-safe',
}


def _run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_runtime_state_snapshot', *args],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )


def test_runtime_snapshot_tool_emits_required_fields_with_runtime_api() -> None:
    result = _run_tool('--package-root', str(PACKAGE_ROOT), '--pretty')
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)

    for field in snapshot_tool.REQUIRED_FIELDS:
        assert field in payload
    assert payload['runtime_state_api_available'] is True
    assert payload['hardware_mutation_enabled'] is False
    assert payload['live_mapping_apply_enabled'] is False
    assert payload['sandbox_is_authoritative'] is False


def test_runtime_snapshot_tool_strict_mode_passes_with_runtime_api() -> None:
    result = _run_tool('--package-root', str(PACKAGE_ROOT), '--strict')
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload['runtime_state_api_available'] is True
    assert payload['validation_summary']['strict_mode'] is True
    assert payload['validation_summary']['strict_fail_reasons'] == []


def test_runtime_snapshot_tool_output_path_and_pretty_json(tmp_path: Path) -> None:
    output_path = tmp_path / 'runtime_state_snapshot.json'
    result = _run_tool(
        '--package-root',
        str(PACKAGE_ROOT),
        '--pretty',
        '--output',
        str(output_path),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert output_path.is_file()
    text = output_path.read_text(encoding='utf-8')
    assert text.startswith('{\n')
    assert '\n  "artifact_id"' in text
    payload = json.loads(text)
    assert payload['validation_summary']['required_fields_present'] is True


def test_runtime_snapshot_tool_include_git_captures_branch_and_commit() -> None:
    payload, exit_code = snapshot_tool.build_runtime_state_snapshot_artifact(
        package_root=PACKAGE_ROOT,
        strict=False,
        include_git=True,
        demo=False,
        provider_override=None,
    )

    assert exit_code == 0
    assert payload['git_branch']
    assert payload['git_commit']


def test_runtime_snapshot_tool_does_not_import_optional_hardware_packages(monkeypatch) -> None:
    for module_name in ('universaldaq_labjack', 'universaldaq_rpi', 'universaldaq_arduino'):
        monkeypatch.delitem(sys.modules, module_name, raising=False)
    snapshot_tool.build_runtime_state_snapshot_artifact(
        package_root=PACKAGE_ROOT,
        strict=False,
        include_git=False,
        demo=False,
        provider_override=None,
    )
    for module_name in ('universaldaq_labjack', 'universaldaq_rpi', 'universaldaq_arduino'):
        assert module_name not in sys.modules
