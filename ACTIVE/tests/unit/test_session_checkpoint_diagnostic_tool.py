from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from tests.conftest import PACKAGE_ROOT
from tools.diagnostics import dump_session_checkpoint as checkpoint_tool

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-DIAG-SESSION-CHECKPOINT-001',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'session checkpoint diagnostic artifact remains non-live and hardware-safe',
}


def _run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_session_checkpoint', *args],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )


def test_checkpoint_tool_default_placeholder_without_api(monkeypatch) -> None:
    monkeypatch.setattr(checkpoint_tool, 'DEFAULT_PROVIDER_CANDIDATES', ('missing.module:missing_provider',))
    payload, exit_code = checkpoint_tool.build_session_checkpoint_artifact(
        package_root=PACKAGE_ROOT,
        strict=False,
        include_git=False,
        demo=False,
        provider_override=None,
    )

    assert exit_code == 0
    assert payload['session_api_available'] is False
    assert payload['warnings']
    for field in checkpoint_tool.REQUIRED_FIELDS:
        assert field in payload
    assert payload['replay_is_live'] is False
    assert payload['hardware_mutation_enabled'] is False
    assert payload['live_mapping_apply_enabled'] is False


def test_checkpoint_tool_strict_fails_without_api(monkeypatch) -> None:
    monkeypatch.setattr(checkpoint_tool, 'DEFAULT_PROVIDER_CANDIDATES', ('missing.module:missing_provider',))
    payload, exit_code = checkpoint_tool.build_session_checkpoint_artifact(
        package_root=PACKAGE_ROOT,
        strict=True,
        include_git=False,
        demo=False,
        provider_override=None,
    )

    assert exit_code == 2
    assert payload['session_api_available'] is False
    assert payload['validation_summary']['strict_fail_reasons']


def test_checkpoint_tool_provider_discovery_when_api_present(monkeypatch) -> None:
    seen_refs: list[str] = []

    def fake_loader(provider_ref: str):
        seen_refs.append(provider_ref)
        if provider_ref == 'universaldaq.session:create_checkpoint_from_runtime_state':

            def _provider() -> dict[str, object]:
                return {
                    'session_model_version': 'udq.session.v1',
                    'session_id': 'S-1',
                    'checkpoint_id': 'C-1',
                    'checkpoint_timestamp': '2026-05-16T00:00:00Z',
                    'runtime_snapshot_id': 'R-1',
                    'runtime_state_model_version': 'udq.runtime.state.v1',
                    'checkpoint_count': 1,
                    'event_count': 4,
                }

            return _provider
        raise ModuleNotFoundError('provider unavailable')

    monkeypatch.setattr(checkpoint_tool, '_load_provider', fake_loader)
    payload, exit_code = checkpoint_tool.build_session_checkpoint_artifact(
        package_root=PACKAGE_ROOT,
        strict=True,
        include_git=False,
        demo=False,
        provider_override=None,
    )

    assert exit_code == 0
    assert payload['session_api_available'] is True
    assert payload['session_checkpoint_provider'] == 'universaldaq.session:create_checkpoint_from_runtime_state'
    assert seen_refs[0] == 'universaldaq.session:create_checkpoint_from_runtime_state'


def test_checkpoint_tool_supports_object_payload_forms(monkeypatch) -> None:
    class WithToDict:
        def to_dict(self) -> dict[str, object]:
            return {'session_model_version': 'demo.v1', 'checkpoint_id': 'A'}

    class WithAsDict:
        def as_dict(self) -> dict[str, object]:
            return {'session_model_version': 'demo.v1', 'checkpoint_id': 'B'}

    class WithModelDump:
        def model_dump(self) -> dict[str, object]:
            return {'session_model_version': 'demo.v1', 'checkpoint_id': 'C'}

    rows: list[Any] = [WithToDict(), WithAsDict(), WithModelDump(), {'session_model_version': 'demo.v1'}]

    def fake_loader(_provider_ref: str):
        row = rows.pop(0)

        def _provider() -> object:
            return row

        return _provider

    monkeypatch.setattr(checkpoint_tool, '_load_provider', fake_loader)
    for _ in range(4):
        payload, exit_code = checkpoint_tool.build_session_checkpoint_artifact(
            package_root=PACKAGE_ROOT,
            strict=False,
            include_git=False,
            demo=False,
            provider_override='custom.provider:build',
        )
        assert exit_code == 0
        assert payload['session_api_available'] is True
        assert payload['session_model_version'] == 'demo.v1'
        assert payload['replay_is_live'] is False
        assert payload['hardware_mutation_enabled'] is False
        assert payload['live_mapping_apply_enabled'] is False


def test_checkpoint_tool_demo_mode_output_path_and_pretty_json(tmp_path: Path) -> None:
    output_path = tmp_path / 'session_checkpoint.json'
    result = _run_tool(
        '--package-root',
        str(PACKAGE_ROOT),
        '--demo',
        '--pretty',
        '--output',
        str(output_path),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert output_path.is_file()
    text = output_path.read_text(encoding='utf-8')
    assert text.startswith('{\n')
    payload = json.loads(text)
    assert payload['session_api_available'] is False
    assert payload['replay_is_live'] is False
    assert payload['hardware_mutation_enabled'] is False
    assert payload['live_mapping_apply_enabled'] is False


def test_checkpoint_tool_does_not_import_optional_hardware_packages(monkeypatch) -> None:
    for module_name in ('universaldaq_labjack', 'universaldaq_rpi', 'universaldaq_arduino'):
        monkeypatch.delitem(sys.modules, module_name, raising=False)

    checkpoint_tool.build_session_checkpoint_artifact(
        package_root=PACKAGE_ROOT,
        strict=False,
        include_git=False,
        demo=False,
        provider_override='missing.module:missing_provider',
    )

    for module_name in ('universaldaq_labjack', 'universaldaq_rpi', 'universaldaq_arduino'):
        assert module_name not in sys.modules
