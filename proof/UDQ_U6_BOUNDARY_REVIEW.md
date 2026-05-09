# UDQ U6 Boundary Review

## Boundary rule
LabJack specifics remain inside `universaldaq_labjack` or tightly related U6 tooling.

## Sprint 2 result
- lifecycle hardening was implemented in `src/universaldaq_labjack/real_u6.py`
- the field-test harness lives under `tools/dev/`
- no universal-core vocabulary was rewritten to become U6-specific
- the frozen public shell/controller surface remains intact

## Residual caution
The hardened U6 line is a specimen for future device work, not a license to let vendor-specific logic drift inward.
