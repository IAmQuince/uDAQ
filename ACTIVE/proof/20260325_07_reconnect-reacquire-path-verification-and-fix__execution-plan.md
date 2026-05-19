# 20260325_07 reconnect-reacquire path verification and fix

## Objective
Align the real-U6 mid-run reconnect branch to the same proven acquisition/open contract that already works for direct-open probing and startup-open smoke.

## Why this sprint exists
- direct-open probing succeeds
- startup-open smoke reaches a healthy live baseline
- guided unplug/replug validation still fails after disconnect because recovery falls through to an older reopen path

## Planned changes
1. trace reconnect strategy choice explicitly per attempt
2. try the proven direct-open reacquire sequence before backend-factory fallback
3. surface reconnect strategy plan/trace in adapter diagnostics and runtime evidence
4. keep startup behavior unchanged
5. rerun targeted contract/integration coverage and governance validators

## Intended validation order
1. direct-open probe
2. startup-open smoke
3. guided unplug/replug validation
