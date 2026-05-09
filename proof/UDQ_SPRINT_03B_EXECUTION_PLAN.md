# UDQ Sprint 03B — U6 Reconnect Correction and Disconnect-Evidence Coherence

## Intent
Sprint 03B is a bounded correction pass on top of the implementation-entry optimization baseline. It does **not** widen the product claim line. It responds directly to the first guided real-U6 return bundle.

## Trigger
The first guided real-U6 field-validation bundle observed a real disconnect, failed to recover in-session, rendered the disconnect window as `configuration_pre_run`, and failed the semantic check that required disconnect-class runtime evidence.

## Correction goals
1. Make same-session U6 reopen/recovery materially more robust without baking LabJack specifics into the universal core.
2. Emit first-class disconnect-incident runtime evidence when the disconnect counter opens.
3. Prevent live-session device loss from rendering as `pre-run / configure` when adapter truth shows degradation/disconnect.
4. Preserve guided harness simplicity while giving real hardware time to re-enumerate before recovery polling begins.
5. Preserve anti-truncation and package-entry discipline.

## Landed code changes
- `src/universaldaq_labjack/real_u6.py`
  - backend opening now honors requested serial selection instead of always taking first-found
  - reconnect open now performs bounded retries before declaring `backend_reopen_failed`
- `src/universaldaq/app/device_lifecycle_handler.py`
  - runtime event spine now emits `device_disconnect_incident_opened` when disconnect count increments
  - degraded adapter state now normalizes the lifecycle summary to `degraded`
- `src/universaldaq/runtime/semantics.py`
  - live-session adapter degradation/disconnect now overrides `ready_to_configure` / `configuration_pre_run` language when those layers disagree
- `tools/dev/_u6_live_support.py`
  - poll runner now supports real-time delay between cycles
- `tools/dev/_u6_field_test_support.py`
  - phase capture now accepts poll pacing
- `tools/dev/run_u6_field_test_harness.py`
  - added `--cycle-delay-seconds`, `--real-cycle-delay-seconds`, and `--reconnect-settle-seconds`
  - real-hardware runs now wait briefly after reconnect before recovery polling
- `tools/dev/run_u6_field_test_harness.bat`
  - fixed the `proofield_tests` path bug
  - aligned launcher defaults with real-hardware pacing and reconnect settle timing

## Landed test changes
- added semantic-precedence coverage for degraded adapter truth overriding configuration language
- tightened recovery-pipeline coverage to require the disconnect-incident event
- added lifecycle-review bundle coverage ensuring degraded incidents no longer render as `ready_to_configure`

## Required next proof step
Run the **same** guided real-U6 harness again. Sprint 03B is a correction pass; it is not a claim that the reconnect defect is closed until the same field test passes.
