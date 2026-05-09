# Correction summary

This sprint keeps the working startup-open seam intact while narrowing reconnect failure attribution.

## Landed changes
- added reconnect strategy plan and attempt trace fields to the real-U6 adapter status snapshot
- changed reconnect reacquire sequencing so the adapter now tries:
  1. verified first-found direct-open probe
  2. verified explicit-serial direct-open probe
  3. backend-factory fallback
- preserved the startup-open path and direct-open probe behavior
- propagated reconnect plan/trace fields into runtime transition evidence for reconnect attempts and backend reopen failures
- added regression coverage proving reconnect can fall through from first-found failure to explicit-serial success without using backend-factory fallback

## Main-app lesson preserved
The deliverable is a clearer canonical lifecycle seam for future device families: reacquire must reuse the same proven acquisition/open contract rather than silently diverging by branch.
