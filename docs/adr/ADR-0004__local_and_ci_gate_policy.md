---
document_id: ADR-0004
title: Local and CI gate policy
revision: r0
status: BASELINE
document_class: architecture_decision_record
owner: UniversalDAQ
depends_on:
  - "UDQ-AUD-SPEC-001"
  - "UDQ-GOV-SPEC-004"
revision_history:
  - "r0 | 2026-03-23 | Registered accepted ADR for the documentation closeout governance pass."
---
# ADR-0004 — Local and CI gate policy

## Status
Accepted

## Decision
Maintain one canonical local gate and one matching CI workflow. CI installs dev dependencies and runs the local gate in strict mode.

## Rationale
Repo quality should not depend on ad hoc local habits or manual memory.

## Consequences
- preferred entrypoint: `python -m tools.dev.run_local_gate --package-root .`
- CI runs the same gate with `--strict-dev-tools`
- audit, type, lint/format, and tests must stay aligned
