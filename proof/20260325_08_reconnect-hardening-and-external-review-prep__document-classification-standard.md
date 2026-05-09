# 20260325_08 — Document Classification Standard

## Purpose
This package uses a strict two-axis document classification model so that `active`, `historical`, `in progress`, and related terms are not left to interpretation.

## Axis A — authority state
Authority answers **where the governing copy lives** and whether the item is currently normative.

Allowed authority states:
- `ACTIVE` — current governing copy
- `ARCHIVED` — no longer governing; retained for traceability
- `RECORD` — execution evidence or review artifact; not a living design/spec document

## Axis B — lifecycle state
Lifecycle answers **what maturity state the content is in**.

Allowed lifecycle states:
- `DRAFT`
- `REVIEW`
- `BASELINE`
- `SUPERSEDED`
- `OBSOLETE`

## Required mapping rules
The following shorthand is no longer allowed as a formal governing status unless explicitly mapped:
- `historical`
- `in progress`
- `current`
- `working`
- `WIP` as a free-floating final status conclusion

Required mappings:
- `historical` => `ARCHIVED + SUPERSEDED` or `ARCHIVED + OBSOLETE`
- `in progress` => `ACTIVE + DRAFT`
- `current governing` => `ACTIVE + BASELINE`
- `execution evidence` => `RECORD`

## Legal combinations
- `ACTIVE + DRAFT`
- `ACTIVE + REVIEW`
- `ACTIVE + BASELINE`
- `ARCHIVED + SUPERSEDED`
- `ARCHIVED + OBSOLETE`
- `RECORD` with a stated role such as proof bundle, audit report, or field-test artifact

## Illegal combinations
- `ACTIVE + SUPERSEDED`
- `ACTIVE + OBSOLETE`
- `ARCHIVED + BASELINE`
- `RECORD + BASELINE`
- any use of `ACTIVE`, `ARCHIVED`, or `RECORD` as vague prose without an explicit mapped meaning on review-entry surfaces

## Directory semantics
- `docs/active/` may contain only `ACTIVE` controlled documents
- `docs/archive/` may contain only `ARCHIVED` controlled documents
- `proof/` and `audit_reports/**` contain `RECORD` artifacts and proof/reporting materials

## README / entry-document exception
README, handbook, and release-entry documents continue to use their own control metadata such as `PRIMARY`, `DERIVED`, and canonical-entry banners. For review interpretation they still map to the two-axis model:
- canonical current entry surfaces => `ACTIVE + BASELINE`
- superseded historical entry surfaces => `ARCHIVED + SUPERSEDED`

## Legacy migration rule
Many controlled files still carry older filename-era `WIP` markers. Until a dedicated migration pass renames and re-registers them, reviewers shall use the two-axis mapping in this document, not the filename suffix alone, to determine authority and maturity.
