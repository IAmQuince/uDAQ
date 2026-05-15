# 20260325_08 generic doctrine vs specimen-specific boundary

## Generic doctrine now supported by the lane
These points should be carried forward as main-app doctrine:
- startup/open failure and mid-run reconnect failure are different lifecycle classes and should remain separate
- the app should own one canonical lifecycle seam spanning discovery, startup/open, first healthy sample, loss detection, recovery, and stabilization
- recovery is not earned merely because an open was attempted; it requires a successful post-loss read and adapter rebound
- stabilization is distinct from recovery and must be proven in its own bounded window
- guided hardware validation should progress in the ordered flow: direct-open primitive, startup-open smoke, guided unplug/replug validation
- package-facing proof must separate authoritative current specimens from historical diagnostic artifacts

## Current specimen-specific realization
These points are true for the present proving specimen, not yet universal platform doctrine:
- the current proving lane uses the LabJack U6 support pack
- the direct-open primitive currently uses the U6-specific constructor/open strategy that succeeded on this machine
- the current field-test artifact folders and filenames are specific to the 20260325 real-U6 runs
- the present reconnect strategy plan and trace names are support-pack-specific implementation details

## Boundary rule
Specimen-specific implementation details are allowed to prove the generic doctrine, but they must not be mistaken for core-platform policy. Future support packs should inherit the lifecycle seam, acceptance shape, and proof pattern, while providing their own minimal specimen-specific open/reconnect realization at the edge.
