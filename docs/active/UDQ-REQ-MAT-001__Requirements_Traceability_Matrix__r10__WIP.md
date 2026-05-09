
# UniversalDAQ — Requirements Traceability Matrix

**Controlled document**  
ID: UDQ-REQ-MAT-001  
Status: ACTIVE  
Revision: r12  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-GOV-GLO-001, UDQ-ARCH-NAR-001, UDQ-ARCH-NAR-002, UDQ-DEV-SPEC-001, UDQ-SIG-SPEC-001, UDQ-OUT-SPEC-001

## Current bounded requirement summary
The active package line now has four bounded requirement groupings that matter most:
1. a repeatable historian/recovery evidence spine,
2. a bounded cross-device read-side acquisition spine,
3. a bounded cross-device write-side command/arbitration slice,
4. a device-centered operator-shell baseline with canonical device-I/O inspection, canonical tag ownership, semantically coded status presentation, and a first executable draft/simulated Logic slice.

## Current active bounded requirement themes
### Historian / recovery baseline
- ordered session evidence, checkpoints, replay, fallback recovery, and repeatability are no longer provisional package aspirations; they are active bounded package truth

### Cross-device read-side closure
- canonical tag projection across multiple adapters is active
- simultaneous mixed-source ingest is active
- mixed-source replay/fallback, degraded adapter behavior, and repeatability are active
- mixed-source variables and review queryability are active

### Cross-device write-side bounded slice
- canonical writable-tag identity is active
- canonical command intents and dispositions are active
- ownership conflicts and stale-expiry handling are active
- target-unavailable rejection is active
- lease revocation on degrade is active
- safe-state-required events are active
- command truth remains inside the same evidence/replay/review spine

## Current requirement-to-proof interpretation
For the current bounded package, requirements should be treated as satisfied only when all three are true:
- implementation exists,
- acceptance or focused proof exists,
- review artifacts can tell the same story without manual reconstruction.

## What remains intentionally open
- controller-backed applied binding mutation and later safe apply from the shell
- authoritative binding availability in all runtime contexts
- true live secondary-axis behavior and richer advanced graph effects
- runtime-authoritative logic deployment beyond the current draft/simulated slice
- broader output breadth, generalized sequencing/orchestration, and broader hardware-family generalization
