# UDQ Sprint 2 — Execution Plan

## Objective
Harden the bounded real LabJack U6 support-pack line without widening the universal core.

## Phases
1. baseline current U6 behavior and support-pack boundaries
2. define an explicit bounded lifecycle contract
3. harden startup and initialization truth
4. harden runtime degradation/disconnect behavior
5. add reviewer-friendly diagnostics and field-test evidence capture
6. close with tests, validators, and updated package-entry surfaces

## Acceptance
- real vs simulated mode remains distinguishable
- startup failure and bounded recovery are test-covered
- a file-based field-test bundle exists for Scott's hardware run
- validators and tests remain green
