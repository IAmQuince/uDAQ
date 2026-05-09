---
document_id: UDQ-LOG-SPEC-001
title: Rules, Conditions, and Actions Specification
revision: r1
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-LOG-001
  - UDQ-ARCH-NAR-001
  - UDQ-ARCH-NAR-002
  - UDQ-REQ-MAT-001
  - UDQ-QUAL-DEF-001
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-UI-INV-001
supersedes:
  - UDQ-LOG-SPEC-001__Rules_Conditions_and_Actions_Specification__r0__WIP.md
---

# Rules, Conditions, and Actions Specification [SEC:UDQ-LOG-SPEC-001::0]

## Revision History [SEC:UDQ-LOG-SPEC-001::0.1]
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-LOG-SPEC-001::1]
This document defines the detailed subsystem specification for UniversalDAQ rules, conditions, and actions. It translates the foundation narratives and UI doctrine into a precise model for how supervisory logic shall be authored, represented, validated, evaluated, traced, and applied.

The intent is to generalize and replace narrow threshold-to-output coupling with a resilient supervisory logic framework that remains understandable to users, backend-authoritative in operation, and auditable in both local and remote workflows.

## 2. Scope [SEC:UDQ-LOG-SPEC-001::2]
This specification governs:
- boolean and numeric signal use in supervisory logic
- derived boolean conditions and reusable condition groups
- rule definitions that bind conditions to actions
- action requests against outputs, virtual states, and workflow triggers
- canonical internal representation for no-code and text-based authoring
- runtime evaluation semantics
- validation and explainability behavior
- interaction with authority, arbitration, interlocks, permissives, safe-state, historian, diagnostics, and UI surfaces

This specification does **not** yet define:
- the full signals and derived-signals schema in detail
- the final output device schema in detail
- full sequence/workflow semantics in detail
- transport/protocol-specific field layouts such as Modbus register mapping

Those are addressed by their own subsystem specifications and must remain compatible with this document.

## 3. Design Intent [SEC:UDQ-LOG-SPEC-001::3]
UniversalDAQ shall support supervisory logic that is:
- more capable than simple over/under threshold coupling
- simpler than full PLC-grade ladder runtime semantics
- understandable by users in visual and structured-text forms
- deterministic and testable
- quality-aware
- backend-owned and backend-evaluated
- auditable and traceable
- safe in the presence of stale, invalid, disconnected, or conflicting inputs

The logic subsystem shall be positioned as a **rule engine for supervisory behavior**, not as an unrestricted scripting surface and not as a claim of PLC equivalence.

## 4. Core Architecture Principle [SEC:UDQ-LOG-SPEC-001::4]
The visual editor and the function-style DSL editor shall be two authoring views over the **same canonical rule model**.

UniversalDAQ shall not maintain separate “simple rules” and “advanced scripted rules” as distinct operational systems if one-to-one round-trip translation is expected.

The canonical model shall be backend-owned. Frontend editors may create, edit, preview, and validate candidate logic, but runtime truth shall derive from the backend’s validated active model.

## 5. Vocabulary [SEC:UDQ-LOG-SPEC-001::5]
## 5.1 Signal [SEC:UDQ-LOG-SPEC-001::5.1]
A named platform value that may be raw, imported, computed, virtual, or stateful, and that has an associated type, value, timestamp, and quality state.

## 5.2 Derived Signal [SEC:UDQ-LOG-SPEC-001::5.2]
A signal computed from other signals. A derived signal may be numeric, boolean, enum-like, or textual as allowed by the signal model.

## 5.3 Condition [SEC:UDQ-LOG-SPEC-001::5.3]
A boolean expression that evaluates to true, false, or blocked/indeterminate depending on value and quality semantics.

## 5.4 Condition Group [SEC:UDQ-LOG-SPEC-001::5.4]
A reusable named boolean construct composed of one or more conditions and/or other condition groups.

## 5.5 Rule [SEC:UDQ-LOG-SPEC-001::5.5]
A named object that binds a target and one or more actions to a condition expression, together with timing, priority, ownership, and operational metadata.

## 5.6 Action [SEC:UDQ-LOG-SPEC-001::5.6]
A structured request for some effect, such as asserting a digital output request, setting an analog target, writing a logical writable point, starting a workflow, or asserting a virtual state.

## 5.7 Rule Evaluation [SEC:UDQ-LOG-SPEC-001::5.7]
The backend process of resolving the current condition state, timing state, and requested action state of a rule.

## 5.8 Rule Activation [SEC:UDQ-LOG-SPEC-001::5.8]
A rule being enabled, validated, loaded into the active runtime model, and participating in evaluation.

## 5.9 Rule Request [SEC:UDQ-LOG-SPEC-001::5.9]
The output of a rule evaluation before arbitration and final authority checks.

## 5.10 Explainability Trace [SEC:UDQ-LOG-SPEC-001::5.10]
The observable chain showing why a rule is true, false, blocked, delayed, inhibited, active, or not currently owning its target.

## 6. Functional Boundaries [SEC:UDQ-LOG-SPEC-001::6]
The rules subsystem shall:
- consume named signals and derived signals
- produce action requests and trace records
- expose validation status and dependency information
- support reusable authoring objects for conditions
- support one-to-one translation between visual authoring and canonical function-style DSL

The rules subsystem shall not:
- directly bypass backend output arbitration
- silently override interlocks, permissives, or safe-state behavior
- depend on frontend-local state as runtime truth
- expose arbitrary unrestricted user code as the primary authoring mechanism

## 7. Logical Layering [SEC:UDQ-LOG-SPEC-001::7]
UniversalDAQ rule logic shall be organized conceptually as:
1. Signals
2. Derived Signals
3. Conditions / Condition Groups
4. Rules
5. Action Requests
6. Output Arbitration / Safe-State / Final Application
7. Historian / Events / Explainability

This ordering is normative. The system shall not collapse authoring and execution concepts in ways that obscure these boundaries.

## 8. Rule Object Model [SEC:UDQ-LOG-SPEC-001::8]
Each rule shall, at minimum, contain the following conceptual fields.

## 8.1 Identity and Metadata [SEC:UDQ-LOG-SPEC-001::8.1]
- stable rule ID
- rule name
- enabled/disabled state
- authoring revision identity
- notes/description
- created/modified metadata
- activation metadata
- tags/category labels as needed

## 8.2 Target Declaration [SEC:UDQ-LOG-SPEC-001::8.2]
The rule shall declare what it is intended to affect. A target may be:
- logical digital output
- logical analog output/setpoint
- writable protocol-backed point
- virtual state bit/flag
- sequence/workflow trigger point
- alarm/event request
- other backend-defined requestable target types approved by architecture

The target shall be a logical platform object, not a raw hardware naming convention as the user-facing primary abstraction.

## 8.3 Condition Expression [SEC:UDQ-LOG-SPEC-001::8.3]
The rule shall contain one condition expression tree. That tree may reference:
- signals
- derived signals
- constants
- condition groups
- approved functions
- approved comparison and boolean operators

## 8.4 Actions [SEC:UDQ-LOG-SPEC-001::8.4]
A rule shall support at least:
- action when condition resolves active/true
- optional action when condition resolves inactive/false

Future extensions may allow additional event-style branches such as on-rising, on-falling, on-fault, on-quality-loss, but the initial canonical model shall remain clean and deterministic.

## 8.5 Timing and Chatter Control [SEC:UDQ-LOG-SPEC-001::8.5]
A rule may define:
- on-delay
- off-delay
- minimum on-time
- minimum off-time
- cooldown/re-arm interval
- hysteresis/deadband where semantically appropriate
- latch/unlatch behavior where approved

## 8.6 Ownership and Priority Metadata [SEC:UDQ-LOG-SPEC-001::8.6]
A rule shall expose metadata needed for arbitration, including:
- nominal rule priority
- applicable modes or contexts
- whether rule requests are advisory, normal, or high-priority within the automatic-rule domain

This metadata does not bypass platform-wide authority doctrine.

## 8.7 Validation State [SEC:UDQ-LOG-SPEC-001::8.7]
Each rule shall carry validation status such as:
- draft / not validated
- valid / inactive
- valid / active
- invalid reference
- invalid type binding
- circular dependency blocked
- target capability mismatch
- runtime suppressed

## 9. Supported Condition Expression Capabilities [SEC:UDQ-LOG-SPEC-001::9]
## 9.1 Basic Node Types [SEC:UDQ-LOG-SPEC-001::9.1]
The canonical expression model shall support:
- signal reference
- constant
- boolean literal
- numeric literal
- string/enum literal where approved
- comparison node
- range node
- boolean ALL group
- boolean ANY group
- boolean NOT node
- function node
- named group reference

## 9.2 Minimum Comparison Set [SEC:UDQ-LOG-SPEC-001::9.2]
The system shall support at minimum:
- EQ
- NE
- LT
- LE
- GT
- GE
- BETWEEN
- OUTSIDE

Textual presentation may render these with user-friendly symbols, but canonical representation shall remain controlled and unambiguous.

## 9.3 Minimum Boolean Set [SEC:UDQ-LOG-SPEC-001::9.3]
The system shall support at minimum:
- ALL(...)
- ANY(...)
- NOT(...)

## 9.4 Minimum Function Set [SEC:UDQ-LOG-SPEC-001::9.4]
The function-style DSL and canonical model shall support at minimum the following or their approved equivalents:
- ABS(...)
- MIN(...)
- MAX(...)
- AVG(...)
- CLAMP(...)
- DIFF(a,b) or equivalent subtract expression form
- GOOD(...)
- VALID(...)
- STALE(...)
- CHANGED(...), if and only if event semantics are clearly defined
- IN_MODE(...)
- DEVICE_ONLINE(...)

Functions may be expanded later, but only under controlled schema revision.

## 9.5 References to Reusable Objects [SEC:UDQ-LOG-SPEC-001::9.5]
The system shall support references to named reusable condition groups and named derived signals, provided dependency and cycle rules are satisfied.

## 10. Condition Semantics [SEC:UDQ-LOG-SPEC-001::10]
## 10.1 Multi-State Resolution [SEC:UDQ-LOG-SPEC-001::10.1]
Internally, condition evaluation shall distinguish at least:
- TRUE
- FALSE
- BLOCKED/INDETERMINATE due to missing, invalid, or disallowed input state

User-facing presentation may phrase BLOCKED/INDETERMINATE more readably, but runtime semantics shall not pretend that unknown inputs are ordinary falsehoods.

## 10.2 Quality Awareness [SEC:UDQ-LOG-SPEC-001::10.2]
Condition semantics shall incorporate data quality. References to stale, invalid, disconnected, or unavailable inputs shall not silently behave as though they are fresh good data.

The system shall support explicit quality-aware predicates so that users may intentionally author logic such as:
- GOOD(Pump_Status)
- NOT(STALE(Pressure_A))
- VALID(Tank_Level)

## 10.3 Default Behavior for Missing Quality Handling [SEC:UDQ-LOG-SPEC-001::10.3]
If a condition references a signal whose quality is not acceptable for the operation being attempted, and the condition does not explicitly tolerate that state, the rule evaluation shall produce a blocked/inhibited result rather than silently treating the bad-quality input as authoritative.

## 10.4 Numeric Behavior [SEC:UDQ-LOG-SPEC-001::10.4]
Numeric comparisons shall operate on normalized engineering values unless a deliberately raw/value-domain reference model is defined elsewhere.

## 10.5 Enum/String Behavior [SEC:UDQ-LOG-SPEC-001::10.5]
Enum-like comparisons shall use controlled value sets. Free-form text comparison shall not be the preferred primary model for runtime-critical decisions.

## 11. Action Model [SEC:UDQ-LOG-SPEC-001::11]
## 11.1 Principle [SEC:UDQ-LOG-SPEC-001::11.1]
A rule action is a **request**, not a direct physical write. Final application requires backend authority, target capability, safety checks, and arbitration.

## 11.2 Minimum Action Types [SEC:UDQ-LOG-SPEC-001::11.2]
The system shall support action types sufficient to cover and generalize existing Genesys behavior plus planned UniversalDAQ expansion, including:
- SET_DIGITAL(target, ON/OFF)
- SET_ANALOG(target, value)
- MAP_ANALOG(target, source/expression)
- WRITE_POINT(target, value)
- PULSE(target, duration)
- START_SEQUENCE(name/id)
- STOP_SEQUENCE(name/id)
- SET_VIRTUAL_STATE(name/id, value)
- RAISE_EVENT(name/id, severity/context)

Not all action types need to be active in the first code implementation, but the model shall support controlled expansion.

## 11.3 True and False Branches [SEC:UDQ-LOG-SPEC-001::11.3]
Each rule shall support:
- ON_TRUE action block
- optional ON_FALSE action block

A missing ON_FALSE action shall not imply arbitrary behavior. The resulting inactive behavior must be well-defined by the target domain, default action semantics, or explicit absence-of-request semantics.

## 11.4 Safe Defaults [SEC:UDQ-LOG-SPEC-001::11.4]
Where a target domain requires a safe fallback value, that value shall be governed by the output/safe-state specification, not by ad hoc per-rule ambiguity.

## 11.5 Expression-Driven Actions [SEC:UDQ-LOG-SPEC-001::11.5]
Where analog or numeric targets are driven from source signals or approved expressions, the action model shall retain a structured form rather than reducing the action to free-form code.

## 12. Timing and Chatter Management [SEC:UDQ-LOG-SPEC-001::12]
The subsystem shall provide timing tools to prevent unstable behavior when input values hover around boundaries or change rapidly.

At minimum the specification shall support:
- on-delay before ON_TRUE becomes active
- off-delay before ON_FALSE or inactive state becomes effective
- minimum dwell times where needed
- hysteresis/deadband for threshold-sensitive conditions or action mappings where appropriate

Timing state shall be visible in explainability surfaces. A user must be able to see when a rule is logically true but not yet active because of an on-delay.

## 13. Arbitration and Ownership Interaction [SEC:UDQ-LOG-SPEC-001::13]
## 13.1 Separation of Concerns [SEC:UDQ-LOG-SPEC-001::13.1]
Rules produce requests. Arbitration resolves which request, if any, owns a target. Final output application then enforces additional safety and capability checks.

## 13.2 Normative Ordering [SEC:UDQ-LOG-SPEC-001::13.2]
The exact authority stack is defined by the outputs/arbitration specification, but this rules subsystem shall assume that automatic-rule requests are only one participant among others such as:
- safe-state override
- interlock/permissive blocking
- manual/operator requests
- sequence-generated requests
- remote-origin requests under policy
- default/fallback behavior

## 13.3 Conflict Visibility [SEC:UDQ-LOG-SPEC-001::13.3]
If multiple rules request incompatible values for the same target, the system shall:
- detect the conflict
- expose the conflict
- resolve ownership via defined arbitration policy
- record the result in trace/event surfaces

Silent last-writer-wins behavior is prohibited.

## 14. Canonical Representation [SEC:UDQ-LOG-SPEC-001::14]
## 14.1 Requirement [SEC:UDQ-LOG-SPEC-001::14.1]
UniversalDAQ shall store rule logic in a canonical structured representation capable of round-trip translation to and from:
- visual rule builder form
- canonical function-style DSL text form

## 14.2 AST Principle [SEC:UDQ-LOG-SPEC-001::14.2]
The canonical representation shall behave as an abstract syntax tree or equivalent graph/tree model, preserving structure, grouping, and semantics.

## 14.3 Structural Preservation [SEC:UDQ-LOG-SPEC-001::14.3]
Round-trip translation shall preserve:
- grouping intent
- function nodes
- references
- constants
- action structure
- timing options
- enable state
- notes/metadata where feasible

The system shall not aggressively rewrite authored logic into a different structural form merely because it is logically similar.

## 15. Function-Style DSL Direction [SEC:UDQ-LOG-SPEC-001::15]
## 15.1 Canonical Style [SEC:UDQ-LOG-SPEC-001::15.1]
The structured text editor shall use a function-style DSL, not ladder and not arbitrary Python.

## 15.2 Example Shape [SEC:UDQ-LOG-SPEC-001::15.2]
Illustrative style only:

```text
RULE "Pump_Enable_Auto"
TARGET DigitalOutput("Pump_Enable")
WHEN ALL(
    IN_MODE("RUN"),
    Tank_Level > 20,
    NOT(STALE(Tank_Level)),
    ANY(
        Temp_1 > 50,
        Temp_2 > 50
    ),
    ABS(DIFF(Pressure_A, Pressure_B)) < 10
)
ON_TRUE SET_DIGITAL("Pump_Enable", ON)
ON_FALSE SET_DIGITAL("Pump_Enable", OFF)
OPTIONS ON_DELAY(2s) OFF_DELAY(5s) PRIORITY(40) ENABLED(TRUE)
```

Exact grammar may evolve in a later schema spec, but the governing principles here are mandatory:
- structured
- controlled
- parseable
- round-trippable
- limited to approved constructs

## 15.3 Prohibited Primary Mode [SEC:UDQ-LOG-SPEC-001::15.3]
Arbitrary embedded Python or unrestricted user scripting shall not be the primary reversible authoring surface for the core rule model.

## 16. Visual Authoring Model [SEC:UDQ-LOG-SPEC-001::16]
The visual editor shall allow users to build and inspect logic without writing text.

The visual authoring model shall support at minimum:
- rule list / library
- rule header/metadata editing
- target selection
- nested ALL/ANY/NOT condition grouping
- signal and derived-signal selection
- reusable condition group references
- true/false action editing
- timing option editing
- enable/disable control
- live evaluation visibility
- validation messages
- dependency visibility

The visual editor shall not be allowed to create constructs that the canonical DSL cannot represent, unless such constructs are explicitly marked non-round-trippable and excluded from the one-to-one contract. The preferred doctrine is to avoid such divergence entirely.

## 17. Dependency and Cycle Rules [SEC:UDQ-LOG-SPEC-001::17]
## 17.1 Allowed Dependencies [SEC:UDQ-LOG-SPEC-001::17.1]
Rules may depend on:
- raw signals
- derived signals
- condition groups
- approved platform state objects

## 17.2 Disallowed or Restricted Dependencies [SEC:UDQ-LOG-SPEC-001::17.2]
The system shall detect and reject or suppress:
- circular dependencies among derived signals and conditions
- circular dependencies among reusable groups
- self-referential rule constructs that require unresolved ordering

## 17.3 Dependency Visibility [SEC:UDQ-LOG-SPEC-001::17.3]
Users shall be able to inspect:
- what inputs a rule depends on
- what reusable groups it consumes
- what targets it affects
- what downstream outputs or behaviors may depend on it indirectly where feasible

## 18. Runtime Evaluation Model [SEC:UDQ-LOG-SPEC-001::18]
## 18.1 Backend Ownership [SEC:UDQ-LOG-SPEC-001::18.1]
Active rule evaluation shall occur in the backend or other authoritative runtime component, not in a frontend-only local interpreter.

## 18.2 Determinism [SEC:UDQ-LOG-SPEC-001::18.2]
Rule evaluation shall be deterministic with respect to the active runtime snapshot, timing semantics, and dependency resolution order defined by the backend.

## 18.3 Evaluation Triggering [SEC:UDQ-LOG-SPEC-001::18.3]
The exact scheduler may be elaborated later, but runtime shall support consistent evaluation in response to:
- relevant input changes
- periodic evaluation ticks where needed
- quality-state changes
- mode changes
- enable/disable changes
- target capability changes where relevant

## 18.4 Snapshot Discipline [SEC:UDQ-LOG-SPEC-001::18.4]
Evaluation should be based on coherent backend state snapshots or well-defined update windows rather than partially mixed local UI reads.

## 19. Explainability and Traceability [SEC:UDQ-LOG-SPEC-001::19]
This subsystem shall be designed so a user can answer:
- Why is this rule true?
- Why is this rule false?
- Why is this rule blocked?
- Why has this rule not yet fired?
- Why did this rule request this target value?
- Why is this rule not currently owning the target?
- Which input changed last?
- What quality problem is inhibiting this rule?

The platform shall therefore expose at minimum:
- current rule truth state
- per-subexpression state where feasible
- active timing state
- inhibition/block reason
- last transition timestamps
- current request value
- arbitration/ownership outcome
- validation status

## 20. UI Implications [SEC:UDQ-LOG-SPEC-001::20]
The UI architecture and interaction model shall provide dedicated support for:
- Signals view
- Derived Signals view
- Conditions / reusable group view
- Rules view
- Action/target binding view
- Live evaluation / trace view
- Validation / diagnostics view
- Text/DSL editor and visual editor as dual surfaces over one model

The UI shall not force users to debug rule behavior only through raw logs. An interactive explainability surface is mandatory.

## 21. Historian, Event, and Audit Implications [SEC:UDQ-LOG-SPEC-001::21]
The system shall record sufficient evidence to support engineering review and release confidence, including as appropriate:
- rule revisions and activation changes
- validation failures
- enable/disable transitions
- target request transitions
- conflict/arbitration outcomes
- blocked/inhibited causes where material
- sequence trigger requests originated by rules

The exact historian/event retention policy belongs to the historian/evidence specification, but the obligation to generate meaningful records is established here.

## 22. Remote Interaction Implications [SEC:UDQ-LOG-SPEC-001::22]
Remote monitoring clients shall be able, subject to deployment policy, to view:
- active rule set status
- rule truth/inhibition state
- live traces and dependencies
- whether rule changes are pending or active

Remote editing or activation, if later enabled, shall be attributable, validated, and subject to the same backend authority and audit trail as local editing.

## 23. Validation Requirements [SEC:UDQ-LOG-SPEC-001::23]
Before activation, the system shall validate at minimum:
- syntax / parse correctness
- reference existence
- type compatibility
- target capability compatibility
- disallowed function use
- cycle detection
- option-value correctness
- mode/ownership applicability where needed

A rule that fails validation shall not silently activate.

## 24. Anti-Patterns [SEC:UDQ-LOG-SPEC-001::24]
The following are explicitly disallowed:
- treating bad-quality inputs as normal false without visibility
- direct rule-to-hardware writes that bypass arbitration
- silent conflict resolution without traceability
- dual authoring systems that cannot round-trip
- unrestricted scripting as the default reversible rule format
- frontend-only rule truth that diverges from backend truth
- hidden delays, hysteresis, or latches
- rule behavior that cannot be explained to a user post hoc

## 25. Minimum Implementation Phasing Guidance [SEC:UDQ-LOG-SPEC-001::25]
The subsystem may be implemented in phases, but each phase shall preserve the canonical architecture.

## Phase A
- generalized threshold/condition engine
- basic visual builder
- canonical rule model
- true/false action blocks
- digital and simple analog targets
- explainability basics

## Phase B
- reusable condition groups
- derived-signal integration
- function-style DSL editor
- round-trip translation
- richer timing options
- writable protocol-backed targets

## Phase C
- advanced mappings
- richer trace surfaces
- remote review/edit workflows under policy
- broader target/action families

A phased implementation shall not introduce architectural dead ends that prevent later canonical DSL/visual parity.

## 26. Requirements Derived from This Specification [SEC:UDQ-LOG-SPEC-001::26]
The following requirement themes shall be carried into the traceability matrix if not already present:
- canonical shared model for visual and DSL authoring
- backend-owned runtime evaluation
- quality-aware condition semantics
- conflict visibility and non-silent arbitration
- explainability trace availability
- target requests rather than direct uncontrolled writes
- reusable condition/derived-signal dependency support
- validation gating before activation

## 27. Definition of Complete Implications [SEC:UDQ-LOG-SPEC-001::27]
The rules subsystem shall not be considered complete unless:
- visual and canonical text authoring are aligned to one model, or the phase explicitly documents temporary limitations without architectural contradiction
- runtime evaluation is backend-authoritative
- stale/invalid input semantics are explicit and testable
- conflicts are visible
- rule behavior can be explained through live inspection surfaces
- activation validation is real, not nominal
- output requests flow through arbitration rather than bypassing it

## 28. Open Items for Follow-On Specs [SEC:UDQ-LOG-SPEC-001::28]
The following should be elaborated in later detailed specifications without contradicting this document:
- full DSL grammar and schema
- exact signal type system and unit semantics
- output target families and capability schemas
- arbitration stack details
- historian/event retention specifics
- remote edit/approval policy
- sequence trigger interaction detail

## 29. Conclusion [SEC:UDQ-LOG-SPEC-001::29]
UniversalDAQ rules, conditions, and actions shall form a readable, auditable, backend-authoritative supervisory logic layer that generalizes existing threshold-coupled behavior into a structured platform capability. The subsystem shall favor canonical structured representation, dual-surface authoring, quality-aware deterministic evaluation, and explainable request generation over ad hoc scripting or PLC mimicry.
