# 20260325_08 lane acceptance criteria

## Scope
These criteria define what it currently means for the bounded real-hardware specimen lane to be considered functionally working.

## Preconditions
- the direct-open primitive succeeds on the real-hardware specimen lane
- the startup-open smoke reaches `live / ready / healthy`
- the guided unplug/replug validation is run on the same bounded package line

## Acceptance criteria
The lane is accepted when the guided unplug/replug validation shows all of the following:
- baseline phase `PASS`
- device-loss phase `PASS`
- recovery phase `PASS`
- post-recovery stabilization phase `PASS`
- `disconnect_count: 1` for the controlled unplug event
- `recovery_count >= 1`
- `session_recovered_after_disconnect: true`
- `post_disconnect_successful_poll_observed: true`
- final reviewer label `live / ready / healthy`
- final state family `live_ready_healthy`
- semantic verdict `PASS`

## Current authoritative specimen
The current lane acceptance specimen is:
- `proof/field_tests/20260325_02_real-u6-guided-unplug-replug-validation`

## What this acceptance does not claim
- it does not prove all support packs are equally ready
- it does not prove generalized multi-device parity
- it does not claim broader output/control depth beyond this bounded specimen line

## Why this matters
This converts the lane from “it worked once” into a governed acceptance shape that can be reused when other hardware specimens are brought up.
