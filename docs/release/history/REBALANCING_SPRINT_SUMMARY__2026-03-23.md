# Rebalancing Sprint Summary — 2026-03-23

**Controlled document**  
ID: UDQ-REL-SUM-REBALANCE-001  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-README-ROOT-001, ADR-0005, ADR-0006, ADR-0007, ADR-0008  

## Scope
This sprint rebalanced the package around a narrow real-value slice and the critique’s highest-leverage maintainability concerns.

## What landed
- narrow real LabJack U6 adapter path for AIN0/AIN1/AIN2
- simulated and real-hardware LabJack U6 smoke commands
- centralized active registry path configuration for tools
- one canonical `tools/_shared.py`
- bounded expression evaluator safeguards
- bounded controller extraction into lifecycle and binding/variable handlers
- shorter contributor procedure and quickstart guidance
- additional ADR coverage around the design choices implemented here

## What stayed intentionally deferred
- streaming depth
- additional device families
- broad UI work
- remote/rules/sequences runtime expansion
- production persistence and deployment concerns
