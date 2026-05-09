# 20260325_08 reconnect hardening and external review prep — Pass B scope boundary

## Purpose
Pass B is a doctrinal capture and traceability pass built on the already-authoritative real-hardware lane. It does not change the now-green startup/open, disconnect, reconnect, or stabilization behavior.

## In scope
- capture the validated lifecycle seam in app terms
- separate generic main-app doctrine from the current LabJack U6 specimen realization
- promote the passing lane into explicit acceptance criteria
- update requirement/spec/proof crosswalks for the now-proven lane
- mark authoritative, historical, and superseded proof artifacts clearly
- update package-entry and review-entry surfaces so tomorrow's external review starts from the right materials
- run documentation/integrity validations and naming/truncation closeout

## Out of scope
- new hardware testing
- reconnect logic changes
- startup/open logic changes
- UI changes
- historian or export redesign
- broad architecture rewriting beyond documenting the validated lifecycle seam

## Pass B working rule
Every new statement in Pass B must either:
1. summarize what the authoritative passing lane now proves,
2. clarify what is reusable for the main app, or
3. improve reviewability and traceability.

If a change does not satisfy one of those three purposes, it should not be part of Pass B.
