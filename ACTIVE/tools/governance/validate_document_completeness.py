from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from tools._registry_paths import active_registry_path
from tools._shared import current_package_id, load_json

MIN_LINE_COUNT_BY_CLASS = {
    'architecture_decision_record': 6,
    'governance_sop': 18,
    'requirement_matrix': 12,
    'gap_report': 12,
    'governance_register': 12,
    'governance_report': 8,
    'consistency_report': 8,
    'controlled_readme': 10,
    'unspecified': 10,
}

SHRINKAGE_GUARDED_CLASSES = {'unspecified', 'governance_register', 'requirement_matrix', 'gap_report', 'governance_sop'}
FORBIDDEN_ACTIVE_ENTRY_PHRASES = {
    'rebalancing remediation baseline',
    'rebalancing and save-point reconciliation baseline',
    'device lifecycle, binding, and variable foundation baseline',
    'stabilization / performance / coherence tightening',
    'stabilization-performance-tightening',
    'savepoint-freeze',
}
ACTIVE_ENTRY_SURFACES = {
    'README.md',
    'docs/handbook/START_HERE.md',
    'docs/handbook/NEXT_ACTIONS.md',
    'docs/handbook/IMPLEMENTATION_ENTRY.md',
    'docs/handbook/TESTS_AND_TOOLS.md',
    'docs/handbook/AUDIT_AND_GOVERNANCE.md',
    'docs/release/EXEC_SUMMARY.md',
    'docs/release/SAVEPOINT_SUMMARY.md',
    'docs/release/RELEASE_NOTES.md',
}
EXTRA_IDENTITY_SURFACES = {'docs/release/RELEASE_MANIFEST.yaml'}


def split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith('---\n'):
        return '', text
    end = text.find('\n---\n', 4)
    if end == -1:
        return '', text
    return text[:end + 5], text[end + 5:]


def count_headings(body: str) -> int:
    return sum(1 for line in body.splitlines() if line.startswith('#'))


def last_nonempty_line(body: str) -> str:
    for line in reversed(body.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
    return ''


def collect_previous_revision_candidates(root: Path, document_id: str) -> list[Path]:
    pattern = f'{document_id}__*.md'
    return sorted((root / 'docs' / 'archive').glob(pattern))


def markdown_cell_count(row: str) -> int:
    in_code = False
    count = 0
    current = ''
    trimmed = row.strip('|')
    for char in trimmed:
        if char == '`':
            in_code = not in_code
            current += char
            continue
        if char == '|' and not in_code:
            count += 1
            current = ''
            continue
        current += char
    return count + 1 if trimmed else 0


def validate_markdown_tables(body: str) -> list[str]:
    findings: list[str] = []
    lines = body.splitlines()
    idx = 0
    while idx < len(lines):
        if not lines[idx].lstrip().startswith('|'):
            idx += 1
            continue
        table: list[str] = []
        start = idx
        while idx < len(lines) and lines[idx].lstrip().startswith('|'):
            table.append(lines[idx].strip())
            idx += 1
        if len(table) < 2:
            findings.append(f'table_too_short_at_line:{start + 1}')
            continue
        separator = table[1]
        if not re.fullmatch(r'\|[\-:| ]+\|', separator):
            findings.append(f'invalid_table_separator_at_line:{start + 2}')
        expected_columns = markdown_cell_count(table[0])
        for row_offset, row in enumerate(table[2:], start=3):
            if '|---|' in row.replace(' ', ''):
                findings.append(f'suspicious_separator_fragment_in_table_row:{start + row_offset}')
            columns = markdown_cell_count(row)
            if columns != expected_columns:
                findings.append(f'table_column_mismatch_at_line:{start + row_offset}:{columns}!={expected_columns}')
    return findings


def collect_completeness_findings(root: Path) -> tuple[list[str], list[dict[str, Any]]]:
    package_id = current_package_id(root)
    loaded = load_json(active_registry_path(root, 'document_json'))
    doc_rows = loaded['rows'] if isinstance(loaded, dict) else loaded
    findings: list[str] = []
    report_rows: list[dict[str, Any]] = []
    for row in doc_rows:
        if row.get('active_state') != 'active':
            continue
        rel = row.get('path', '')
        path = root / rel
        if not rel.endswith('.md') or not path.exists():
            continue
        text = path.read_text(encoding='utf-8')
        _fm, body = split_front_matter(text)
        lines = list(body.splitlines())
        nonempty = [ln for ln in lines if ln.strip()]
        heading_count = count_headings(body)
        last_line = last_nonempty_line(body)
        doc_class = row.get('document_class', 'unspecified') or 'unspecified'
        min_lines = MIN_LINE_COUNT_BY_CLASS.get(doc_class, 12)
        status = 'PASS'
        notes: list[str] = []

        if len(nonempty) < min_lines:
            status = 'FAIL'
            notes.append(f'nonempty_line_count_below_threshold:{len(nonempty)}<{min_lines}')
        if heading_count < 2:
            status = 'FAIL'
            notes.append(f'heading_count_too_low:{heading_count}')
        if last_line.startswith('#') or last_line in {'|', '```'}:
            status = 'FAIL'
            notes.append('abrupt_terminal_line')

        table_findings = validate_markdown_tables(body)
        if table_findings:
            status = 'FAIL'
            notes.extend(table_findings)

        previous_candidates = collect_previous_revision_candidates(root, row['document_id'])
        prev_sizes = []
        prev_headings = []
        for candidate in previous_candidates:
            body_prev = split_front_matter(candidate.read_text(encoding='utf-8'))[1]
            prev_sizes.append(len(body_prev))
            prev_headings.append(count_headings(body_prev))
        if prev_sizes:
            max_prev_size = max(prev_sizes)
            max_prev_headings = max(prev_headings) if prev_headings else 0
            if (
                doc_class in SHRINKAGE_GUARDED_CLASSES
                and len(body) < max_prev_size * 0.25
                and heading_count < max(3, int(max_prev_headings * 0.5))
            ):
                status = 'FAIL'
                notes.append('severe_shrinkage_vs_archive')
        else:
            max_prev_size = 0
            max_prev_headings = 0

        report_rows.append(
            {
                'document_id': row['document_id'],
                'path': rel,
                'document_class': doc_class,
                'body_char_count': len(body),
                'heading_count': heading_count,
                'archive_reference_char_count': max_prev_size,
                'archive_reference_heading_count': max_prev_headings,
                'status': status,
                'notes': '; '.join(notes) if notes else 'OK',
            }
        )
        if status != 'PASS':
            findings.append(f"document completeness failure: {row['document_id']} -> {rel} ({'; '.join(notes)})")

    for rel in sorted(ACTIVE_ENTRY_SURFACES | EXTRA_IDENTITY_SURFACES):
        path = root / rel
        if not path.exists():
            findings.append(f'missing identity surface: {rel}')
            continue
        text = path.read_text(encoding='utf-8')
        lowered = text.lower()
        if rel in ACTIVE_ENTRY_SURFACES and package_id not in text:
            findings.append(f'active entry surface missing current package id: {rel}')
        for phrase in FORBIDDEN_ACTIVE_ENTRY_PHRASES:
            if phrase in lowered:
                findings.append(f'active entry surface contains forbidden stale phrase: {rel} -> {phrase}')

    governance_model_path = active_registry_path(root, 'governance_model_json')
    if not governance_model_path.exists():
        findings.append('missing identity surface: governance_model_json')
    else:
        governance_text = governance_model_path.read_text(encoding='utf-8')
        if package_id not in governance_text:
            findings.append('active identity surface missing current package id: governance_model_json')
        lowered = governance_text.lower()
        for phrase in FORBIDDEN_ACTIVE_ENTRY_PHRASES:
            if phrase in lowered:
                findings.append(f'active identity surface contains forbidden stale phrase: governance_model_json -> {phrase}')

    return findings, report_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--report-json', default='')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    findings, rows = collect_completeness_findings(root)
    if args.report_json:
        report_path = root / args.report_json
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps({'rows': rows, 'findings': findings}, indent=2) + '\n', encoding='utf-8')
        print(report_path)
    if findings:
        for item in findings:
            print(item)
        return 1
    print('PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
