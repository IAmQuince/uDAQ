# 20260326_05 Richer Recovery and Longer Bounded Session Sprint

## What landed
- longer bounded populated specimen session with 12 cycles and richer hot/warm/cold historian content
- stronger checkpoint spacing for the main specimen lane with non-zero replay tails preserved
- richer corrupted-checkpoint fallback scenario that now forces recovery from an earlier valid checkpoint instead of trivially reusing the same checkpoint id
- fallback recovery artifacts now include:
  - `fallback_recovery_detail.json` / `fallback_recovery_detail.md`
  - `session_timeline.json` / `session_timeline.md`
- reviewability artifacts now also include `session_timeline.json` / `session_timeline.md`
- acceptance automation upgraded to assert:
  - minimum fallback replay tail depth
  - multi-type fallback replay coverage
  - fallback state-hash validity
  - recovery review artifact presence

## Bundled acceptance proof
- `proof/acceptance/20260327_001239/acceptance_report.json`
- `proof/acceptance/20260327_001239/acceptance_report.md`
- `proof/acceptance/20260327_001239/reviewability/review_summary.json`
- `proof/acceptance/20260327_001239/reviewability/replay_detail.json`
- `proof/acceptance/20260327_001239/reviewability/checkpoint_ladder.json`
- `proof/acceptance/20260327_001239/reviewability/session_timeline.json`
- `proof/acceptance/20260327_001239/fault_injection/fallback_recovery_detail.json`
- `proof/acceptance/20260327_001239/fault_injection/session_timeline.json`

## Acceptance result
- verdict: PASS
- main replay tail count: 15
- main replay tail record types: cycle, runtime_event, sample, variable_update
- main checkpoint sequence ids: 36, 72
- fallback corrupted checkpoint id: `CHK-SESSION-FAULT-INJECTION-107-58`
- fallback recovered checkpoint id: `CHK-SESSION-FAULT-INJECTION-103-29`
- fallback replay tail count: 37
- fallback replay tail record types: cycle, runtime_event, sample, variable_update

## Focused validation
- targeted replay/recovery acceptance tests: 6 passed
- one-command acceptance runner: PASS

## Main operator entry
```bat
c:\Users\iaq16\Documents\Code\tenThousand\.venv\Scripts\python.exe tools\acceptance\run_evidence_acceptance.py --package-root .
```
