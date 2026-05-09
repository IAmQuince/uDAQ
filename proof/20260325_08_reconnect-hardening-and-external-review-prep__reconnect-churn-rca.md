# 20260325_08 reconnect hardening and external-review prep — Reconnect churn RCA

## Question
Why did the authoritative passing guided unplug/replug validation recover only after multiple reconnect attempts instead of on the first reconnect attempt?

## Evidence reviewed
- `proof/field_tests/20260325_02_real-u6-guided-unplug-replug-validation/20260325_02_real-u6-guided-unplug-replug-validation__events.csv`
- `proof/field_tests/20260325_02_real-u6-guided-unplug-replug-validation/20260325_02_real-u6-guided-unplug-replug-validation__diagnostics.json`
- `proof/field_tests/20260325_02_real-u6-guided-unplug-replug-validation/20260325_02_real-u6-guided-unplug-replug-validation__summary.txt`

## Findings
1. The lane is functionally green.
   - The run ends with a successful recovery, successful post-disconnect polling, successful adapter rebound, and a healthy live stabilized posture.
2. The repeated reconnect failures happen during the intentional device-loss window, before the operator reconnect prompt.
   - The observed reconnect-attempt failures cluster immediately after the unplug confirmation.
   - The harness does not prompt reconnect until later, after the loss-observation window has completed.
3. A reconnect-settle wait is already present before recovery polling after the reconnect prompt.
4. The eventual successful reconnect uses the proven direct/verified constructor path, not the legacy fallback path.

## Conclusion
The observed reconnect-attempt churn in the passing specimen is not evidence of a still-broken recovery path after replug. It is a bounded timing artifact produced by the harness intentionally continuing to poll during the loss window before the operator is asked to reconnect the device.

## Pass A disposition
- No reconnect algorithm redesign is justified in Pass A.
- The churn is recorded as a non-blocking timing artifact.
- Any future reconnect hardening should be driven only by evidence of churn that continues after the reconnect prompt and settle window, not by the pre-replug attempts observed in the current passing specimen.
