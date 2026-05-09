from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping


def _hash_payload(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(dict(payload), sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def verify_session_artifacts(session_root: Path) -> dict[str, object]:
    journal_dir = session_root / 'journal'
    checkpoint_dir = session_root / 'checkpoints'
    manifest_path = journal_dir / 'manifest.json'
    findings: list[str] = []
    checks: list[dict[str, object]] = []
    segment_rows: list[dict[str, object]] = []
    all_entries: list[dict[str, object]] = []

    manifest_exists = manifest_path.exists()
    checks.append({'name': 'manifest_exists', 'status': 'PASS' if manifest_exists else 'FAIL'})
    if not manifest_exists:
        findings.append('missing manifest.json under journal/')
        return {
            'session_root': str(session_root),
            'verdict': 'FAIL',
            'checks': checks,
            'findings': findings,
            'segment_rows': segment_rows,
            'entry_count': 0,
            'checkpoint_rows': [],
        }

    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    expected_last_sequence = int(manifest.get('last_sequence_id', 0) or 0)
    for row in manifest.get('segments', []):
        segment_rows.append(dict(row))
        segment_path = journal_dir / str(row.get('relative_path', ''))
        exists = segment_path.exists()
        checks.append(
            {
                'name': f"segment_exists::{row.get('segment_id', 'unknown')}",
                'status': 'PASS' if exists else 'FAIL',
            }
        )
        if not exists:
            findings.append(f"missing segment file: {segment_path.name}")
            continue
        for raw_line in segment_path.read_text(encoding='utf-8').splitlines():
            if not raw_line.strip():
                continue
            all_entries.append(json.loads(raw_line))

    ordered_sequences = [int(row.get('sequence_id', 0) or 0) for row in all_entries]
    sequence_continuity = ordered_sequences == list(range(1, len(ordered_sequences) + 1))
    checks.append({'name': 'sequence_continuity', 'status': 'PASS' if sequence_continuity else 'FAIL'})
    if not sequence_continuity:
        findings.append('sequence ids are not contiguous starting at 1')

    manifest_alignment = (0 if not ordered_sequences else ordered_sequences[-1]) == expected_last_sequence
    checks.append({'name': 'manifest_last_sequence_alignment', 'status': 'PASS' if manifest_alignment else 'FAIL'})
    if not manifest_alignment:
        findings.append('manifest last_sequence_id does not match final persisted entry')

    checkpoint_rows: list[dict[str, object]] = []
    latest_checkpoint_path = checkpoint_dir / 'latest.json'
    for checkpoint_path in sorted(checkpoint_dir.glob('CHK-*.json')):
        try:
            payload = json.loads(checkpoint_path.read_text(encoding='utf-8'))
            payload_hash_valid = str(payload['state_hash']) == _hash_payload(dict(payload.get('payload', {})))
            checkpoint_rows.append(
                {
                    'checkpoint_id': str(payload['checkpoint_id']),
                    'path': checkpoint_path.name,
                    'hash_valid': payload_hash_valid,
                    'last_committed_sequence_id': int(payload.get('last_committed_sequence_id', 0) or 0),
                }
            )
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            checkpoint_rows.append({'path': checkpoint_path.name, 'hash_valid': False, 'parse_error': True})

    valid_checkpoint_count = sum(1 for row in checkpoint_rows if bool(row.get('hash_valid')))
    checks.append({'name': 'checkpoint_available', 'status': 'PASS' if valid_checkpoint_count > 0 else 'FAIL'})
    if valid_checkpoint_count == 0:
        findings.append('no valid checkpoint files found')

    latest_checkpoint_valid = False
    if latest_checkpoint_path.exists():
        try:
            latest_payload = json.loads(latest_checkpoint_path.read_text(encoding='utf-8'))
            latest_checkpoint_valid = str(latest_payload['state_hash']) == _hash_payload(dict(latest_payload.get('payload', {})))
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            latest_checkpoint_valid = False
    checks.append({'name': 'latest_checkpoint_hash_valid', 'status': 'PASS' if latest_checkpoint_valid else 'WARN'})
    if latest_checkpoint_path.exists() and not latest_checkpoint_valid:
        findings.append('latest checkpoint is invalid; fallback path required')

    verdict = 'PASS' if all(check['status'] in {'PASS', 'WARN'} for check in checks if check['name'] != 'latest_checkpoint_hash_valid') else 'FAIL'
    return {
        'session_root': str(session_root),
        'verdict': verdict,
        'checks': checks,
        'findings': findings,
        'segment_rows': segment_rows,
        'entry_count': len(all_entries),
        'checkpoint_rows': checkpoint_rows,
        'latest_checkpoint_path': str(latest_checkpoint_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--session-root', required=True)
    parser.add_argument('--json-output')
    args = parser.parse_args()

    report = verify_session_artifacts(Path(args.session_root).resolve())
    if args.json_output:
        output_path = Path(args.json_output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"verify-session-artifacts: verdict={report['verdict']} entries={report['entry_count']} checkpoints={len(report['checkpoint_rows'])}")
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
