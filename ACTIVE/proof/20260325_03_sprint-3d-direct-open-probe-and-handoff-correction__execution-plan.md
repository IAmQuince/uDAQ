# Sprint 3D — direct-open probe and startup-handoff correction

## Goal
Resolve the main-app startup-open seam by separating direct hardware probe from controller discovery/open, and by aligning the production U6 startup-open path with a proven explicit-serial open sequence.

## App-facing deliverables
- reusable direct-open probe pattern for support-pack bring-up
- clearer startup-open classification at the app/runtime boundary
- optional prevalidated probe rows so discovery does not need to re-open hardware just to rediscover it
- continued startup-smoke gating before any reconnect/recovery work
