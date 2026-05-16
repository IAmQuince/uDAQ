from __future__ import annotations

from pathlib import Path

from universaldaq.runtime import build_authoritative_runtime_snapshot


def test_authoritative_runtime_state_has_no_vendor_or_write_path_imports() -> None:
    source = Path('src/universaldaq/runtime/state.py').read_text(encoding='utf-8')

    forbidden_tokens = (
        'universaldaq_labjack',
        'universaldaq_arduino',
        'universaldaq_rpi',
        'request_write',
        'apply_to_sandbox',
        'AdapterCommandRequest',
    )
    assert not any(token in source for token in forbidden_tokens)


def test_authoritative_runtime_state_default_snapshot_is_non_actuating() -> None:
    payload = build_authoritative_runtime_snapshot(timestamp=700).to_dict()

    assert payload['command_posture']['authority_enabled'] is False
    assert payload['logic_posture']['authority_enabled'] is False
    assert payload['applied_state']['value']['authoritative_mapping_count'] == 0
