# UniversalDAQ Architecture Status

## Current architecture shape

### Core platform
The universal core owns:
- runtime truth handling
- signal and variable evaluation
- bounded runtime metrics
- events/alarms
- command admission
- rules/sequences orchestration
- governed-action claims and correlation
- journaling and review surfaces

### Support packs
Support packs are optional edge integrations. In the current proof line this includes:
- generic adapter inventory
- LabJack support pack
- bounded Arduino and Raspberry Pi support-pack scaffolds

### Proof harnesses
Device-specific proof harnesses live in `tools/dev` and are not the product identity.

## What is implemented now
- bounded live-value slice on the real U6
- reconnect/degraded recovery semantics with explicit reconnect-stage evidence
- same-run unplug/replug recovery demonstrated on the bounded real-U6 specimen line
- transition-based events/alarms with acknowledgment
- official command-entry lane with admitted and rejected proof paths
- rules/sequences skeleton that emits command intent only through command admission
- governed-action claims that suppress duplicate orchestration and preserve correlation
- synchronized package-facing evidence and review-entry surfaces after the documentation-alignment pass

## Universality statement
The intended architecture remains vendor-agnostic in the core. The current proof environment demonstrates the right shape by discovering generic adapters alongside the LabJack support pack, but broader hardware generalization is still only partially proven.

## Boundedness statement
The current proof is intentionally narrow:
- one bounded real-U6 read-side specimen
- bounded command/event/orchestration semantics
- bounded runtime metrics and queues
- bounded file-based field-test evidence rather than broad operational telemetry depth
