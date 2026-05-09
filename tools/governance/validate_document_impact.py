from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_FILES = [
    '.github/PULL_REQUEST_TEMPLATE/typed_domain_model_sprint.md',
    '.github/ISSUE_TEMPLATE/implementation_change.yml',
    '.github/ISSUE_TEMPLATE/docs_change.yml',
    'docs/active/UDQ-GOV-SOP-001__Controlled_Document_Update_and_Impact_Process__r4__WIP.md',
    'docs/active/UDQ-GOV-TPL-001__Sprint_Documentation_Impact_Checklist__r2__WIP.md',
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md',
    'docs/active/UDQ-IMP-PLAN-001__Implementation_Transition_and_Handoff_Plan__r7__WIP.md',
    'docs/active/UDQ-GOV-WI-001__Step_by_Step_Document_Reconciliation_and_Logging_Work_Instruction__r0__WIP.md',
    'docs/active/UDQ-GOV-TPL-002__Documentation_Review_and_Outcome_Ledger_Template__r0__WIP.md',
    'docs/active/UDQ-GOV-POL-002__README_Control_and_Classification_Policy__r0__WIP.md',
    'CONTRIBUTING.md',
    'docs/handbook/IMPLEMENTATION_ENTRY.md',
    'docs/handbook/NEXT_ACTIONS.md',
    'README.md',
    'docs/release/RELEASE_NOTES.md',
]

REQUIRED_PHRASES = {
    'CONTRIBUTING.md': [
        'documentation impact map',
        'required review payload',
        'update order',
        'controlled readmes',
        'udq-gov-reg-003',
        'udq-gov-wi-001',
        'udq-gov-tpl-002',
    ],
    'docs/handbook/IMPLEMENTATION_ENTRY.md': [
        'phase 0',
        'phase 4',
        'save point',
    ],
    'docs/handbook/NEXT_ACTIONS.md': [
        'reconciliation',
        'phase 3',
    ],
    'README.md': [
        'save-point reconciliation baseline',
        'still intentionally deferred',
    ],
}


def validate(root: Path) -> list[str]:
    findings: list[str] = []
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            findings.append(f'missing required document-impact asset: {rel}')
    for rel, phrases in REQUIRED_PHRASES.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8').lower()
        missing = [phrase for phrase in phrases if phrase not in text]
        if missing:
            findings.append(f'{rel} missing required phrases: {missing}')
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    findings = validate(root)
    if findings:
        for item in findings:
            print(item)
        return 1
    print('document-impact validation: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
