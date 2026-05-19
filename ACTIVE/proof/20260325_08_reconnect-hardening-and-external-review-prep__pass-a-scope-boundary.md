# 20260325_08 reconnect hardening and external-review prep — Pass A scope boundary

## Purpose
Pass A is a bounded technical-hardening pass on an already green real-U6 lifecycle lane. It does not reopen the startup/open or reconnect defect lines.

## In scope
- explain the reconnect-attempt churn observed in the passing guided unplug/replug validation
- disposition the remaining startup-smoke advisory in a way that matches the actual authoritative evidence surfaces
- preserve the current green behavior in direct-open probe, startup-open smoke, and guided unplug/replug validation
- stage the current authoritative proof bundles so tomorrow's external review can inspect the green lane from one package

## Out of scope
- new hardware permutations
- UI work
- historian redesign
- reconnect algorithm redesign
- new LabJack-only policy in app core
- broad semantics or evidence-model expansion

## Pass A decision rule
Any change in this pass must either reduce reviewer ambiguity or reduce technical ambiguity without destabilizing the current green specimen.
