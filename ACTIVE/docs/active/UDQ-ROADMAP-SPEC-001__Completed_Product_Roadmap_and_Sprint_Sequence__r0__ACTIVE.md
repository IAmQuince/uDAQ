# Completed Product Roadmap and Sprint Sequence

**Controlled document**  
ID: UDQ-ROADMAP-SPEC-001  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-IMP-PLAN-001, UDQ-GAP-RPT-001, UDQ-QUAL-DEF-001, UDQ-LIFECYCLE-SPEC-001, UDQ-OUT-SPEC-001, UDQ-UI-SPEC-004  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Purpose

This document defines the broad completed-product roadmap for UniversalDAQ and establishes the controlled sprint sequence that should guide work after Sprint Zero. It is intentionally product-level rather than task-level: `NEXT_ACTIONS.md` remains the immediate next-action surface, and `WORKPLAN_CURRENT_RUN.md` remains the active-run surface.

## Completed-product definition

UniversalDAQ is complete enough for an initial product release when it can operate as a device-agnostic DAQ, historian, logic, and control workbench with safe authority boundaries. The product must let an operator discover devices, map raw device I/O into canonical signals, graph live and historical data, author and validate logic, arbitrate output command intents, persist and restore sessions, survive degraded conditions, export evidence/review bundles, and support optional hardware/protocol packs without contaminating the universal core.

## Capability maturity levels

| Level | Name | Meaning |
|---|---|---|
| 0 | Documented | Requirement/specification exists, but no executable proof is present. |
| 1 | Simulated proof | Behavior is proven against simulated or static inputs. |
| 2 | Sandbox proof | Behavior mutates isolated sandbox state with rollback and audit evidence. |
| 3 | Runtime proof | Behavior operates against live runtime state without direct physical hazard. |
| 4 | Hardware-in-loop proof | Behavior is validated with real devices under controlled degraded conditions. |
| 5 | Release candidate | Behavior is packaged, documented, tested, and ready for external review. |

## Major product subsystems

| Subsystem | Completion expectation |
|---|---|
| Core runtime state | Single authoritative state tree for devices, points, mappings, signals, variables, logic posture, command posture, and UI projections. |
| Device/protocol abstraction | Optional support packs declare capabilities and never leak vendor assumptions into the core. |
| Mapping and binding | Raw hardware points can be bound to canonical signals through reviewable, reversible, audited workflows. |
| Acquisition runtime | Live acquisition supports timestamps, quality, stale/fault/degraded status, reconnect, backpressure, and graceful shutdown. |
| Historian/replay/export | Durable storage supports indexed samples, events, checkpoints, replay, selected export, and evidence bundles. |
| Graphing/review workbench | Live, historical, sliding-window, explore, replay, trace styling, decimation, and export all behave truthfully. |
| Logic Designer | Rules can be drafted, validated, simulated, reviewed, and deployed only through governed command-intent pathways. |
| Command arbitration/output authority | Physical writes require controller authority, ownership leases, safety checks, interlocks, and audit trails. |
| Sequences/workflows | Procedures support preview, start/stop/reset, steps, waits, conditions, timeouts, safe abort, and evidence. |
| Diagnostics/watchdog/health | Device, service, historian, queue, command, reconnect, and dependency health are visible and exportable. |
| UI shell/workspaces | Dockable/resizable panels, saved layouts, restore defaults, settings persistence, and diagnostics export are first-class. |
| Remote observation | Remote surfaces observe selected state/history without unintended command authority. |
| Packaging/release governance | Every release is cleanly zipped, path-budgeted, documented, validated, and externally reviewable. |
| Hardware-in-loop validation | Real devices are tested for unplug/replug, simultaneous degradation, stale data, denial, safe-state, and long-run stability. |

## Controlled sprint sequence

| Sprint | Status | Title | Primary unlock |
|---:|---|---|---|
| 0 | complete in this package | Roadmap and governance stabilization | Clean planning/governance baseline |
| 1 | planned | Sandbox mapping mutation proof | Reversible apply/rollback without live hardware authority |
| 2 | planned | Authoritative runtime state model | Single source of truth for runtime and UI projections |
| 3 | planned | Durable session/checkpoint/replay spine | Crash-tolerant reconstruction and replay |
| 4 | planned | Live acquisition runtime | Canonical live samples with health/quality states |
| 5 | planned | Device Explorer / Signal Explorer integration | Clear device/raw-point/signal/variable separation |
| 6 | planned | Controlled live mapping apply boundary | Live mapping updates through preflight/review/commit/rollback |
| 7 | planned | Historian production layer | Indexed history, retention, replay, and exports |
| 8 | planned | Graphing and review workbench | Truthful live/historical plotting and review |
| 9 | planned | Logic Designer draft/simulate/validate | Safe rule authoring before live deployment |
| 10 | planned | Runtime logic deployment boundary | Live monitoring and governed command-intent emission |
| 11 | planned | Output authority and safe-state execution | Safe writes, ownership leases, interlocks, and observed confirmation |
| 12 | planned | Sequences and workflows | Reviewable procedural automation |
| 13 | planned | Modbus support pack | First-class Modbus TCP/RTU capability pack |
| 14 | planned | Diagnostics/watchdog/health dashboard | Operator-visible degraded-condition posture |
| 15 | planned | UI shell polish and persistence | Durable bench-application experience |
| 16 | planned | Remote observation/review mode | Non-authoritative remote visibility |
| 17 | planned | Hardware-in-loop validation suite | Real-device degraded-condition confidence |
| 18 | planned | Packaging/installer/release governance | Distributable release mechanics |
| 19 | planned | External review and release-candidate hardening | Initial release-candidate closure |

## Dependency and do-not-start gates

| Gate | Rule |
|---|---|
| Live mapping apply | Do not start before sandbox mapping mutation proof and authoritative runtime state model are complete. |
| Runtime logic deployment | Do not start before logic draft/simulate/validate and command arbitration boundaries are complete. |
| Physical output authority | Do not start before command ownership, inhibit/interlock, safe-state, and observed-confirmation semantics are defined and tested. |
| Historian production | Do not claim production history until replay, indexing, export, corruption handling, and long-run behavior are validated. |
| UI polish as capability claim | Do not let a polished UI imply runtime authority that is not implemented. UI must expose draft/simulated/review-only/live/degraded/blocked posture. |
| Support-pack expansion | Do not introduce vendor/protocol details into the universal core. Support packs declare capabilities through adapter contracts. |
| Remote observation | Do not expose remote command authority until observation-only behavior is explicitly separated and tested. |

## Roadmap change control

The roadmap may be revised, but only through a documented sprint, reconciliation pass, or external-review response. Any revision must update this document, the sprint sequence register, `NEXT_ACTIONS.md`, relevant release notes, and any affected known limitations or debt records.

## Sprint register authority

The machine-readable sprint sequence register in `registries/active/universalDAQ_sprint_sequence_register_r0.json` is the audit-facing copy of this sequence. The CSV version is provided for human review and spreadsheet inspection. This document explains the sequence; the register tracks sprint metadata, preconditions, non-goals, risks, mitigations, and acceptance summaries.
