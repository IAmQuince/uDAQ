# 20260325_06 reconnect-path alignment correction — scope boundary

## In scope
- Real-U6 reconnect reacquisition and reopen behavior after a live-session device loss.
- App-level lifecycle state transitions from disconnected -> recovering -> recovered.
- Runtime evidence needed to explain reconnect strategy choice and first post-loss successful poll.
- Regression tests for startup-good / reconnect-bad / reconnect-corrected behavior.

## Out of scope
- New hardware families.
- UI redesign or new operator controls.
- Historian or bundle redesign beyond what the reconnect seam already emits.
- Extra hardware permutation testing unless a corrected rerun still demands it.

## App-level relevance test
This sprint is valid only because it tightens the generic main-app seam:
`discover -> select active adapter -> startup/open -> live poll -> device loss -> reacquire -> first healthy post-loss poll`.
LabJack remains the proving specimen, not the product center of gravity.
