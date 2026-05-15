# Run 8 Plan — 20260323_08_integration_success_path

## Purpose
Add one safe successful sequence completion path while preserving the existing clean sequence failure path.

## Scope
- Keep runtime/value/event/alarm/command predicates green.
- Add `SEQ-U6-AUTOACK` as a successful sequence path using `ack_alarm` through command admission.
- Preserve `SEQ-U6-DRYRUN` as the negative-path proof.
- Keep all orchestration-generated actions on the official command-admission path.

## Success criteria
- One sequence reaches `completed`.
- One sequence still reaches `failed`.
- Command summary shows both admitted and rejected command paths.
- Real-U6 runtime remains bounded.
