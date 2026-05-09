# Bounded Long-Run Characterization and Recovery Stress Release Notes

- Extended the bounded specimen historian run to a deeper long-run profile with 18 cycles and a 4-cycle checkpoint cadence.
- Added long-run characterization artifacts so acceptance proves record depth, checkpoint depth, and bounded query/review behavior in one place.
- Added a repeatability gate that reruns the bounded specimen lane three times and fails if depth or replay metrics drift.
- Deepened corrupted-latest-checkpoint recovery stress so fallback recovery now proves a richer multi-type replay tail from a deeper checkpoint ladder.
- Kept the operator surface bounded: the main one-command acceptance entry remains unchanged.
