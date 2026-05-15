# universaldaq.commands

Bounded command-admission spine for UniversalDAQ.

This package owns the official shell-side entry lane for command intent:
- command request identity and attribution
- admission or rejection outcome
- dry-run / non-actuating proof paths
- review-bundle summaries for recent command decisions

It intentionally does **not** yet implement broad command arbitration, multi-actor ownership,
sequence dispatch, or rich UI tooling.
