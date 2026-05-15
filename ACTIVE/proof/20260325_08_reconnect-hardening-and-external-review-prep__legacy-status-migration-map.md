# 20260325_08 — Legacy Status Migration Map

## Problem
A large portion of the controlled corpus still uses older filename-era `__WIP` markers and front-matter `status: WIP` values. Those markers are no longer sufficient by themselves to communicate authority and lifecycle.

## Immediate package-line rule
For the current external-review package, interpret legacy materials using the stricter two-axis model:
- path under `docs/active/` => `ACTIVE`
- path under `docs/archive/` => `ARCHIVED`
- path under `proof/` or `audit_reports/**` => `RECORD`
- legacy `WIP` wording on a current active doc => treat as `DRAFT` unless an entry surface or package note explicitly identifies it as the current bounded baseline for this package line

## Known current exceptions
- many active controlled specs remain filename-marked `__WIP` even when review-entry surfaces rely on them as current material
- canonical package-entry READMEs and review-entry documents use README-control language in addition to the two-axis mapping

## Deferred migration work
A later dedicated governance cleanup pass should:
1. rename active controlled docs away from legacy `__WIP` markers where appropriate
2. align front-matter status values to the stricter lifecycle enum
3. regenerate registries with explicit authority/lifecycle columns
4. retire or archive superseded package-entry surfaces more aggressively
