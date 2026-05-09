# UDQ Run 5 Plan — Rules/Sequences Spine

## Goal

Create the first thin orchestration layer that can:
- observe canonical runtime/event/alarm truth,
- emit governed command intent,
- force that intent through the existing command-admission spine,
- and journal the whole chain without introducing a bypass path.

## Mandatory opening cleanup included in this run

1. **Variable-change summary naming**
   - separate requested / impacted / evaluated / value_changed / state_changed reviewer-facing counts.

2. **Event-counter naming split**
   - distinguish domain event/alarm transitions from broader runtime events.

3. **Journal path display**
   - shorten reviewer-facing path display to a proof/runtime-relative path.

## Scope

### Rules
- bounded rule definition model
- evaluate canonical runtime truth
- emit governed command intent
- duplicate-safe recent rule rows

### Sequences
- bounded sequence definition model
- minimal statuses: idle / running / completed / failed / stopped
- wait-step support on canonical alarm truth
- command-emission step support through official command admission only
- recent sequence rows

### Controller integration
- register_rule_definition(...)
- register_sequence_definition(...)
- start_sequence(...)
- evaluate_automation(...)

### Review surfaces
- rule_summary
- sequence_summary
- recent_rule_rows
- recent_sequence_rows

## Proof scenario

1. bounded U6 live slice is active
2. reconnect-style degraded state raises the existing alarm
3. one rule emits an `ack_alarm` command through official command admission
4. the alarm becomes acknowledged
5. one sequence waits on the alarm lifecycle and then emits a dry-run adapter command
6. the dry-run command is rejected for unsupported capability
7. sequence failure is recorded cleanly

## Out of scope
- broad real actuation
- scheduler
- rich automation DSL
- multi-device orchestration
- editor/dashboard UI expansion
