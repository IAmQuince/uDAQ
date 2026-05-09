# Release Notes — 20260326_04 Non-Zero Tail Replay and Bounded Specimen Depth

## Highlights
- The main populated-session replay proof now exercises a non-zero checkpoint tail.
- The replay tail contains multiple record types rather than a single post-checkpoint event.
- Review artifacts now include replay detail and checkpoint ladder summaries.
- Acceptance automation continues to provide a one-command verification path.

## Operator entry
From the package root on Windows Command Prompt:

```bat
c:\Users\iaq16\Documents\Code\tenThousand\.venv\Scripts\python.exe tools\acceptance\run_evidence_acceptance.py --package-root .
```

## Expected result
A successful run prints:

```text
evidence-acceptance: verdict=PASS report_dir=...
```

and writes an acceptance bundle under `proof/acceptance/`.

## Acceptance additions
The acceptance runner now verifies:
- populated historian counts
- non-zero replay tail
- multi-type replay tail
- checkpoint ladder spacing
- review summary, replay detail, and checkpoint ladder artifacts
