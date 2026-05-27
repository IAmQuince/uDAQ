# Contributing to UniversalDAQ

## Purpose
UniversalDAQ is still a bounded pre-production package, so contributions should favor clear delivered value, low churn, and strong automated proof. The current priority is the narrow real-device LabJack U6 slice plus the maintainability and safety fixes that support it.

## Working rules
- Do not expand scope into new device families, streaming engines, deep historian work, remote/rules/sequences, or broad UI polish unless the active sprint explicitly says so.
- Keep vendor specifics inside support packs and keep the universal core vendor-agnostic.
- Prefer thin orchestration, typed models, and regression-backed changes over broad rewrites.
- Do not remove public behavior or frozen interfaces without an ADR or explicit sprint decision.

## Practical contributor flow
1. Read `README.md`, `docs/handbook/START_HERE.md`, and `docs/handbook/QUICKSTART_CONTRIBUTOR.md`.
2. Confirm the change fits the current sprint scope.
3. Check the documentation impact map and identify the one authoritative status record you need to update.
4. Follow the update order from `docs/active/UDQ-GOV-WI-001__Step_by_Step_Document_Reconciliation_and_Logging_Work_Instruction__r0__WIP.md` (`UDQ-GOV-WI-001`) and record any still-open items in `docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md`.
5. Update only the directly impacted docs, tests, and proof artifacts, and use `docs/active/UDQ-GOV-TPL-002__Documentation_Review_and_Outcome_Ledger_Template__r0__WIP.md` for the required review payload when a human pass is needed.
6. Run `python -m tools.dev.run_local_gate --package-root .`.
7. If the change touches the LabJack slice, also run `python -m tools.dev.run_labjack_u6_smoke --package-root .` in simulated mode and note whether a real-device check is still pending.

## Required update discipline
For ordinary bug fixes or bounded features, update:
- the code,
- the directly affected tests,
- the sprint/release summary,
- and only the docs that actually changed meaning.

Do not treat every bounded code change as a trigger to touch broad governance surfaces. The automated validators and local gate remain required; the manual procedure is intentionally lighter for this sprint line.

## Review payload
A review package should show:
- what changed,
- why it changed,
- what tests and proof artifacts were run,
- whether the LabJack real-device smoke remains pending or was verified,
- and what is intentionally deferred.

## Controlled documentation references
The controlled READMEs and handbook entrypoints remain part of the contributor path, but this sprint compresses the manual burden: keep the controlled readmes in sync with the active sprint summary, follow the update order, and treat the documentation impact map plus the required review payload as the minimum manual checklist rather than expanding broad governance edits by default.

Validator phrase anchors: `udq-gov-reg-003`, `udq-gov-wi-001`, and `udq-gov-tpl-002`.

## Deferred documentation handling
When a bounded code change cannot immediately update every related controlled document, record the intentionally deferred docs in `docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md` and note the review ledger entry or review ledger payload used to explain the deferral.
