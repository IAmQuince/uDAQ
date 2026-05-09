# 20260325_08 reconnect hardening and external-review prep — Startup advisory disposition

## Original advisory
The startup-open smoke previously ended `PASS WITH ADVISORIES` because the semantic checker required explicit startup/open-class runtime rows in the bounded recent-event window.

## Observation
The authoritative startup-open smoke already contains authoritative startup-open evidence on other surfaces:
- active adapter status reports `has_successful_startup_open=true`
- startup-open attempt/success counters are populated
- the baseline phase reaches `live_ready_healthy`
- the preflight direct-open probe succeeded

## Pass A decision
Pass A treats successful startup-open counters on the final active-adapter status as authoritative startup-open evidence when the bounded recent-event window has already rolled past the initial startup rows.

## Rationale
This keeps the semantic checker aligned with the actual authoritative review surfaces without widening the runtime-event window or changing startup behavior.

## Resulting posture
The startup-open smoke can now pass cleanly when startup-open is clearly proven by counters and final adapter state, even if explicit startup/open rows are no longer present in the recent runtime-event slice.
