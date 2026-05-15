from __future__ import annotations

import argparse
import re
from pathlib import Path

from tools._shared import canonical_review_entry

REQUIRED_FILES = [
    'proof/20260325_08_reconnect-hardening-and-external-review-prep__document-classification-standard.md',
    'proof/20260325_08_reconnect-hardening-and-external-review-prep__document-classification-matrix.md',
    'proof/20260325_08_reconnect-hardening-and-external-review-prep__legacy-status-migration-map.md',
    'proof/20260325_08_reconnect-hardening-and-external-review-prep__artifact-authority-map.md',
    'docs/release/EXEC_SUMMARY.md',
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md',
]

REQUIRED_STANDARD_PHRASES = {
    'proof/20260325_08_reconnect-hardening-and-external-review-prep__document-classification-standard.md': [
        'ACTIVE', 'ARCHIVED', 'RECORD', 'DRAFT', 'REVIEW', 'BASELINE', 'SUPERSEDED', 'OBSOLETE',
        'legacy', 'WIP', 'two-axis'
    ],
    'proof/20260325_08_reconnect-hardening-and-external-review-prep__document-classification-matrix.md': [
        'Illegal combinations', 'ACTIVE + BASELINE', 'ARCHIVED + SUPERSEDED', 'RECORD'
    ],
    'proof/20260325_08_reconnect-hardening-and-external-review-prep__legacy-status-migration-map.md': [
        'filename-era', 'docs/active/', 'docs/archive/', 'proof/'
    ],
    'docs/release/EXEC_SUMMARY.md': [
        'Document-classification rule for review', 'legacy `WIP` filename markers'
    ],
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md': [
        'UDQ-DOC-DEBT-004', 'legacy filename/front-matter status carryover'
    ],
}

FORBIDDEN_STATUS_WORDS = {'historical', 'in progress', 'current', 'working'}


def validate(root: Path) -> list[str]:
    findings: list[str] = []
    current_review = str(canonical_review_entry(root))
    required_files = [*REQUIRED_FILES, current_review]
    required_phrases = {
        **REQUIRED_STANDARD_PHRASES,
        current_review: ['Mandatory classification rule for this review', 'ACTIVE', 'ARCHIVED', 'RECORD'],
    }
    for rel in required_files:
        path = root / rel
        if not path.exists():
            findings.append(f'missing classification asset: {rel}')
            continue
        text = path.read_text(encoding='utf-8')
        lowered = text.lower()
        for phrase in required_phrases.get(rel, []):
            if phrase.lower() not in lowered:
                findings.append(f'{rel} missing required phrase: {phrase}')
    review_start = (root / current_review).read_text(encoding='utf-8')
    if 'legacy filename suffixes like `__WIP` are not authoritative by themselves' not in review_start and 'legacy filename suffixes like `__WIP` are not authoritative by themselves' not in (root / 'docs/release/EXEC_SUMMARY.md').read_text(encoding='utf-8'):
        findings.append('review surfaces do not explicitly reject filename-suffix-only interpretation')
    # Guard against informal status labels being presented as formal states in the standard.
    standard = (root / 'proof/20260325_08_reconnect-hardening-and-external-review-prep__document-classification-standard.md').read_text(encoding='utf-8').lower()
    for word in FORBIDDEN_STATUS_WORDS:
        pattern = rf'formal governing status.*{re.escape(word)}'
        if re.search(pattern, standard):
            findings.append(f'classification standard still appears to allow ambiguous governing term: {word}')
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate strict document-classification assets for the current review package.')
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    findings = validate(root)
    if findings:
        for item in findings:
            print(item)
        return 1
    print('document-classification validation: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
