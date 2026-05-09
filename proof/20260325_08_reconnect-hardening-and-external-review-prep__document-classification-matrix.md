# 20260325_08 — Document Classification Matrix

| Authority state | Lifecycle state | Meaning | Allowed location | Governing? |
|---|---|---|---|---|
| ACTIVE | DRAFT | current working draft under active development | `docs/active/` | Yes, but provisional |
| ACTIVE | REVIEW | current document under formal review | `docs/active/` | Yes, pending review outcome |
| ACTIVE | BASELINE | current bounded truth / accepted working procedure | `docs/active/`, canonical current entry surfaces | Yes |
| ARCHIVED | SUPERSEDED | replaced historical copy retained for traceability | `docs/archive/`, archival entry surfaces | No |
| ARCHIVED | OBSOLETE | no longer applicable except as history | `docs/archive/` | No |
| RECORD | n/a | execution evidence or proof artifact | `proof/`, `audit_reports/active/`, `audit_reports/archive/` | No |

## Illegal combinations
| Combination | Why illegal |
|---|---|
| ACTIVE + SUPERSEDED | a current governing copy cannot already be replaced |
| ACTIVE + OBSOLETE | a current governing copy cannot already be obsolete |
| ARCHIVED + BASELINE | archived material is not the current baseline |
| RECORD + BASELINE | proof artifacts are not living baseline specs |

## Reviewer translation table
| Legacy phrase seen in old material | Required interpretation |
|---|---|
| historical | ARCHIVED + SUPERSEDED or ARCHIVED + OBSOLETE |
| in progress | ACTIVE + DRAFT |
| canonical current | ACTIVE + BASELINE |
| proof artifact / field test / audit output | RECORD |
| filename suffix `__WIP` on current controlled docs | legacy marker only; determine real authority/lifecycle from the active/archive location and current review-entry notes |
