from __future__ import annotations

import argparse
from pathlib import Path
import csv

from tools._registry_paths import active_registry_path
from tools._shared import canonical_review_entry, load_json, parse_assignment
from tools._time import timestamp_slug
from tools.governance.validate_document_completeness import collect_completeness_findings


REQUIRED_ROOTS = [
    'README.md',
    'pyproject.toml',
    '.pre-commit-config.yaml',
    'CONTRIBUTING.md',
    'CODEOWNERS',
    '.github/workflows/ci.yml',
    '.github/PULL_REQUEST_TEMPLATE/typed_domain_model_sprint.md',
    '.github/ISSUE_TEMPLATE/implementation_change.yml',
    '.github/ISSUE_TEMPLATE/docs_change.yml',
    'docs/handbook/START_HERE.md',
    'docs/release/EXEC_SUMMARY.md',
    'docs/handbook/PUBLIC_API_FREEZE.md',
    'docs/handbook/IMPLEMENTATION_ENTRY.md',
    'docs/handbook/TESTS_AND_TOOLS.md',
    'docs/handbook/AUDIT_AND_GOVERNANCE.md',
    'docs/handbook/NEXT_ACTIONS.md',
    'docs/review/SAVEPOINT_DISCREPANCY_INVENTORY.md',
    'docs/review/SAVEPOINT_REVIEW_LEDGER.md',
    'docs/review/HUMAN_PASS_CHECKLIST.md',
    'docs/release/RELEASE_MANIFEST.yaml',
    'docs/release/PACKAGE_ENTRY_REGISTRY.yaml',
    'docs/release/RELEASE_NOTES.md',
    'docs/release/SAVEPOINT_SUMMARY.md',
    'docs/active/UDQ-IMP-GUIDE-001__Python_Typing_and_Modeling_Policy__r0__WIP.md',
    'docs/active/UDQ-SEC-BASELINE-001__Security_and_Trust_Boundary_Baseline__r0__WIP.md',
    'docs/active/UDQ-SCHEMA-POLICY-001__Governance_Schema_Conventions__r0__WIP.md',
    'docs/active/UDQ-GOV-SOP-001__Controlled_Document_Update_and_Impact_Process__r4__WIP.md',
    'docs/active/UDQ-GOV-TPL-001__Sprint_Documentation_Impact_Checklist__r2__WIP.md',
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md',
    'docs/active/UDQ-GOV-POL-002__README_Control_and_Classification_Policy__r0__WIP.md',
    'docs/active/UDQ-GOV-WI-001__Step_by_Step_Document_Reconciliation_and_Logging_Work_Instruction__r0__WIP.md',
    'docs/active/UDQ-GOV-TPL-002__Documentation_Review_and_Outcome_Ledger_Template__r0__WIP.md',
    'docs/active/UDQ-GOV-SOP-002__Controlled_Document_Completeness_and_Recovery_Process__r0__WIP.md',
    'docs/active/UDQ-IMP-PLAN-001__Implementation_Transition_and_Handoff_Plan__r7__WIP.md',
    'tools/governance/validate_document_debt.py',
    'tools/governance/validate_package_entry_surfaces.py',
    'tools/governance/validate_document_completeness.py',
    'tools/governance/validate_document_impact.py',
    'tools/governance/validate_readme_control.py',
    'tools/traceability/dump_requirement_to_code_and_test_links.py',
    'tools/dev/run_shell_smoke.py',
]

REQUIRED_DIRS = [
    'tests/meta', 'tests/smoke', 'tests/contract', 'tests/scenario', 'tests/invariants', 'tests/integration',
    'tests/fixtures', 'tests/data', 'tools/governance', 'tools/traceability', 'tools/audit',
    'tools/diagnostics', 'tools/package_build', 'tools/proof', 'tools/dev', 'src/universaldaq/signals',
    'src/universaldaq/app', 'src/universaldaq/common', 'src/universaldaq/outputs', 'src/universaldaq/events',
    'src/universaldaq/historian', 'src/universaldaq/profiles', 'src/universaldaq/ui', 'docs/adr', 'docs/handbook',
    'docs/release', 'docs/review',
]

RESERVED_DIRS = [
    'src/universaldaq/backend', 'src/universaldaq/diagnostics',
    'src/universaldaq/remote',
]

FORBIDDEN_ROOT_NAMES = {
    'README_START_HERE.md', 'README_EXEC_SUMMARY.md', 'README_IMPLEMENTATION_ENTRY.md', 'README_TESTS_AND_TOOLS.md',
    'README_NEXT_ACTIONS.md', 'README_AUDIT_AND_GOVERNANCE.md', 'README_RUN_AUDIT.md', 'README_HUMAN_PASS.md',
    'UDQ_RELEASE_MANIFEST.yaml', 'UDQ_RELEASE_NOTES.md', 'sitecustomize.py', 'udq_master_audit_v7.py',
    'udq_master_audit_v8.py', 'udq_master_audit_v9.py', 'UDQ_MASTER_AUDIT__2026-03-21_235959.md',
}

def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if '|' in value:
            return [part.strip() for part in value.split('|') if part.strip()]
        if ',' in value:
            return [part.strip() for part in value.split(',') if part.strip()]
        stripped = value.strip()
        return [stripped] if stripped else []
    return [value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--profile', default='live-runtime-integration-and-safe-control-posture-foundations')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    findings: list[str] = []

    required_roots = [*REQUIRED_ROOTS, str(canonical_review_entry(root))]
    for rel in required_roots:
        if not (root / rel).exists():
            findings.append(f'missing required asset: {rel}')

    for rel in REQUIRED_DIRS:
        if not (root / rel).exists():
            findings.append(f'missing required directory: {rel}')

    for name in sorted(FORBIDDEN_ROOT_NAMES):
        if (root / name).exists():
            findings.append(f'forbidden root-level artifact present: {name}')

    for rel in RESERVED_DIRS:
        path = root / rel
        if not (path / 'README.md').exists():
            findings.append(f'missing reserved-package guardrail README: {rel}/README.md')
        allowed = {'README.md', '__init__.py', '.gitkeep'}
        extra = sorted(p.name for p in path.iterdir() if p.is_file() and p.name not in allowed)
        if extra:
            findings.append(f'reserved package contains active files: {rel} -> {extra}')

    req = load_json(active_registry_path(root, 'requirement_json'))
    inv = load_json(active_registry_path(root, 'invariant_json'))
    contract = load_json(active_registry_path(root, 'execution_contract_json'))
    cov = load_json(active_registry_path(root, 'implementation_coverage_json'))
    gov = load_json(active_registry_path(root, 'governance_model_json'))
    worked = load_json(root / 'tests/data/first_slice_worked_examples.json')
    readmes = load_json(active_registry_path(root, 'readme_json'))

    req_rows = req['requirements'] if isinstance(req, dict) else req
    valid_req = {row['requirement_id'] for row in req_rows}
    valid_inv = {row['invariant_id'] for row in inv['rows']}
    valid_exm = {row['worked_example_id'] for row in worked['examples']}

    contract_rows = contract['entries'] if isinstance(contract, dict) else contract
    for row in contract_rows:
        if row['requirement_id'] not in valid_req:
            findings.append(f"execution contract references unknown requirement: {row['requirement_id']}")
        missing_inv = sorted(set(_as_list(row.get('expected_invariant_ids', []))) - valid_inv)
        if missing_inv:
            findings.append(f"execution contract {row['requirement_id']} missing invariants: {missing_inv}")

    for row in cov['rows']:
        if row['implementation_entry_status'] == 'READY_FOR_IMPLEMENTATION':
            if row['test_stub_status'] not in {'SCAFFOLDED', 'IMPLEMENTED'}:
                findings.append(f"ready requirement without scaffolded tests: {row['requirement_id']}")
            if row['snapshot_status'] != 'GENERATED':
                findings.append(f"ready requirement without generated snapshot: {row['requirement_id']}")
            if row['local_guardrail_status'] != 'PRESENT':
                findings.append(f"ready requirement without local guardrail: {row['requirement_id']}")

    for path in sorted((root / 'tests').rglob('test_*.py')):
        decl = parse_assignment(path, 'TEST_DECLARATION')
        missing_req = sorted(set(decl.get('verifies_requirements', [])) - valid_req)
        missing_inv = sorted(set(decl.get('checks_invariants', [])) - valid_inv)
        example = decl.get('worked_example_reference')
        if missing_req:
            findings.append(f'{path.relative_to(root)} unknown requirements: {missing_req}')
        if missing_inv:
            findings.append(f'{path.relative_to(root)} unknown invariants: {missing_inv}')
        if example and example not in valid_exm:
            findings.append(f'{path.relative_to(root)} unknown worked example: {example}')

    for row in readmes.get('rows', []):
        if not (root / row['path']).exists():
            findings.append(f"readme registry references missing document: {row['path']}")

    completeness_findings, _completeness_rows = collect_completeness_findings(root)
    findings.extend(completeness_findings)

    loaded_docs = load_json(active_registry_path(root, 'document_json'))
    doc_rows = loaded_docs['rows'] if isinstance(loaded_docs, dict) else loaded_docs
    edge_rows = list(csv.DictReader(open(active_registry_path(root, 'cross_reference_edges_csv'), newline='', encoding='utf-8')))
    edge_docs = {row['source_document_id'] for row in edge_rows} | {row['target_document_id'] for row in edge_rows}
    for row in doc_rows:
        path_value = row.get('path', '')
        doc_id = row.get('document_id', '')
        revision = row.get('revision', '')
        status = row.get('status', '')
        active_state = row.get('active_state', '')
        if not path_value or not (root / path_value).exists():
            findings.append(f"document registry path missing on disk: {doc_id or '<blank-id>'} -> {path_value}")
            continue
        if not doc_id:
            findings.append(f"document registry row missing document_id: {path_value}")
        if not revision:
            findings.append(f"document registry row missing revision: {doc_id or '<blank-id>'} -> {path_value}")
        if not status:
            findings.append(f"document registry row missing status: {doc_id or '<blank-id>'} -> {path_value}")
        if active_state == 'active' and doc_id and doc_id not in edge_docs:
            findings.append(f"active document missing cross-reference graph participation: {doc_id}")
        if path_value.startswith('docs/active/') and doc_id and '__' in Path(path_value).name:
            stem = Path(path_value).name.split('__', 1)[0]
            if stem != doc_id:
                findings.append(f"active controlled filename/id mismatch: {doc_id} -> {path_value}")
    disposition = 'IMPLEMENTATION_ENTRY_READY' if not findings else 'IMPLEMENTATION_DRIFT'
    audit_status = 'PASS_CLEAN' if not findings else 'FAIL'
    timestamp = timestamp_slug()
    report = root / f'audit_reports/active/UDQ_MASTER_AUDIT__{timestamp}.md'
    lines = [
        '# UniversalDAQ Master Audit',
        '',
        f'- profile: {args.profile}',
        f"- package_id: {gov['package_id']}",
        f'- package_disposition: {disposition}',
        f'- audit_status: {audit_status}',
        f'- findings: {len(findings)}',
        '',
    ]
    if findings:
        lines.append('## Findings')
        lines.extend(f'- {item}' for item in findings)
    else:
        lines.extend(['## Result', 'PASS_CLEAN'])
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(report)
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
