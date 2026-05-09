# UDQ Sprint 03B — Correction Summary

## What changed
Sprint 03B is the narrow response to the first guided real-U6 field-validation failure. The package now:
- opens the real U6 by requested serial when available,
- retries bounded backend open during reconnect,
- records a first-class disconnect-incident runtime event,
- normalizes degraded live-session device loss to `degraded` rather than `ready_to_configure`,
- uses adapter truth over configuration language when those layers materially disagree,
- waits briefly after reconnect so Windows/USB re-enumeration can complete before recovery polling begins,
- and fixes the batch-launcher output path bug.

## What Sprint 03B does not claim
- it does not claim that the field reconnect defect is fully closed yet,
- it does not widen the hardware scope,
- it does not convert the package into a broad architecture rewrite.

## Required next step
Execute the same guided real-U6 field-validation harness and compare the new bundle directly against the frozen failure specimen.
