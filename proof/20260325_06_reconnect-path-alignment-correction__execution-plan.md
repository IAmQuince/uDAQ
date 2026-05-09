# 20260325_06 reconnect-path alignment correction — execution plan

## Objective
Correct the remaining app-level reconnect seam after startup/open was proven healthy in real mode.

## Boundaries
- Preserve the now-working startup-open path.
- Align mid-run reconnect reacquisition to the same proven acquisition/open path.
- Keep the change inside the specimen support-pack seam used by the main app lifecycle pipeline.
- Do not broaden into UI, historian, or unrelated device work.

## Planned order
1. Freeze the working startup and failing reconnect specimens.
2. Trace the reconnect branch against the working startup branch.
3. Correct reconnect reacquisition to prefer the proven direct-open/verified-serial path.
4. Tighten regression coverage around startup-good / reconnect-bad splits.
5. Revalidate with the same guided unplug/replug flow after startup smoke remains green.
