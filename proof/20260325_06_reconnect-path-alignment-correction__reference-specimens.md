# 20260325_06 reconnect-path alignment correction — reference specimens

## Working startup specimens
- `20260325_04_real-u6-direct-open-probe`
- `20260325_01_real-u6-startup-open-smoke`

These runs proved that the app could discover a real U6, open it, perform a first read, and reach `live / ready / healthy`.

## Failing reconnect specimen
- `20260325_02_real-u6-guided-unplug-replug-validation`

This run proved that disconnect detection and evidence were working, but reconnect reacquisition still failed and the session ended disconnected.

## Governing diagnosis
The reconnect branch diverged from the working startup branch by falling back to `open_all_match_serial` instead of reusing the proven first-found acquisition path with serial verification.
