# 20260325_08 reconnect hardening and external-review prep — Pass A hardening summary

## What Pass A did
- froze the current authoritative green real-U6 specimens inside this package
- explained the reconnect-attempt churn seen in the passing guided run as a pre-replug timing artifact of the intentional loss window
- dispositioned the startup-smoke advisory by aligning semantic validation with authoritative startup-open counters on the final adapter status
- left the now-green startup/open and reconnect/recovery path behavior unchanged

## What Pass A did not do
- no new hardware investigation
- no reconnect redesign
- no UI or historian changes
- no architecture widening

## Outcome
Pass A leaves this lane technically cleaner and easier to review:
- current green proof specimens are staged inside the package
- the startup-open semantic story is cleaner
- the remaining reconnect-attempt churn is documented as non-blocking and bounded
