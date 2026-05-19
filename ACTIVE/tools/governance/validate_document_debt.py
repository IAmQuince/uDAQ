from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_FILES = [
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md',
    'docs/active/UDQ-GOV-SOP-001__Controlled_Document_Update_and_Impact_Process__r4__WIP.md',
    'docs/active/UDQ-GOV-TPL-001__Sprint_Documentation_Impact_Checklist__r2__WIP.md',
    'CONTRIBUTING.md',
    'docs/active/UDQ-GOV-WI-001__Step_by_Step_Document_Reconciliation_and_Logging_Work_Instruction__r0__WIP.md',
    'docs/active/UDQ-GOV-TPL-002__Documentation_Review_and_Outcome_Ledger_Template__r0__WIP.md',
]

REQUIRED_PHRASES = {
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md': [
        'reviewed, found stale',
        'intentionally deferred',
        'status |',
    ],
    'docs/active/UDQ-GOV-SOP-001__Controlled_Document_Update_and_Impact_Process__r4__WIP.md': [
        'material documentation drift is not allowed to remain invisible',
        'udq-gov-reg-003',
        'deferred-update rule',
        'running review ledger',
    ],
    'CONTRIBUTING.md': [
        'intentionally deferred docs',
        'udq-gov-reg-003',
        'udq-gov-wi-001',
        'review ledger',
    ],
    'docs/active/UDQ-GOV-WI-001__Step_by_Step_Document_Reconciliation_and_Logging_Work_Instruction__r0__WIP.md': [
        'step-by-step procedure',
        'every reviewed controlled asset shall end the bounded change with exactly one outcome',
        'no reviewed asset may remain without an outcome',
    ],
}



def validate(root: Path) -> list[str]:
    findings: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            findings.append(f'missing required document-debt asset: {rel}')
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
    print('document-debt validation: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
