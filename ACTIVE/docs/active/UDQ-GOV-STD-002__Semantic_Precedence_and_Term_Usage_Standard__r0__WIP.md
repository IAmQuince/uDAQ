---
document_id: UDQ-GOV-STD-002
title: Semantic Precedence and Term Usage Standard
revision: r0
status: WIP
document_class: governance_standard
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-GLO-001
  - UDQ-GOV-MAP-001
revision_history:
  - "r0 | 2026-03-21 | Initial issue establishing semantic ownership, precedence, alias rules, contradiction handling, and duplication classification."
---
# Semantic Precedence and Term Usage Standard {#gov-std-002.s01}

## 1. Purpose [SEC:UDQ-GOV-STD-002::1]

This standard defines how semantic meaning is owned, inherited, narrowed, checked, and corrected across the controlled UniversalDAQ corpus.

## 2. Precedence stack [SEC:UDQ-GOV-STD-002::2]

From highest to lowest, semantic precedence shall be:

1. governance standards and canonical glossary
2. document architecture/dependency governance
3. foundation architecture narratives
4. subsystem specifications
5. UI specifications and detail surface specifications
6. templates, reports, and machine-readable registers derived from controlled docs
7. readmes and package guidance

A lower-precedence document may clarify or narrow a term for context, but it shall not silently redefine a higher-precedence meaning.

## 3. Term ownership rule [SEC:UDQ-GOV-STD-002::3]

Every project-critical term shall have one canonical owning definition. The owning definition shall be declared in the glossary or in another explicitly nominated higher-precedence document.

## 4. Allowed narrowing [SEC:UDQ-GOV-STD-002::4]

A subordinate document may narrow a term only when all of the following are true:

- the owning definition is still valid,
- the narrowed usage is explicitly contextual,
- the narrowed usage does not invert the parent meaning,
- the narrowed usage does not create a competing default meaning elsewhere.

## 5. Alias rule [SEC:UDQ-GOV-STD-002::5]

Allowed aliases shall be explicitly declared in the term-usage matrix. Disallowed aliases shall not appear in normative language except when being identified as problematic usage.

## 6. Contradiction classes [SEC:UDQ-GOV-STD-002::6]

- **CONTRADICTION** — two controlled sources make mutually incompatible normative claims.
- **AMBIGUITY** — a term or behavior can be read in more than one materially different way.
- **NARROWING_ALLOWED** — a lower document applies a constrained local usage without changing the parent meaning.
- **OPEN_DECISION** — a project choice is intentionally unresolved and must not be treated as settled truth.
- **STYLE_ONLY** — wording differs without changing semantic meaning.

## 7. Duplication classes [SEC:UDQ-GOV-STD-002::7]

- **INTENTIONAL_REFERENCE_DUPLICATION** — repeated material exists to preserve local readability and does not create competing truth.
- **GOVERNED_BOILERPLATE** — repeated headings or standard scaffolding intentionally recur across document families.
- **SHADOW_DEFINITION** — a lower-precedence document repeats a definition in a way that risks becoming a second owner.
- **CONSOLIDATE_REQUIRED** — materially overlapping prose should be reduced or relocated.

## 8. Required treatment of contradictions [SEC:UDQ-GOV-STD-002::8]

A contradiction shall not remain silently embedded in active controlled documents. It shall either be resolved in the affected documents or elevated into an explicit open decision that blocks downstream reliance on the disputed meaning.

## 9. Required treatment of duplication [SEC:UDQ-GOV-STD-002::9]

Duplication is acceptable only when classified and governed. Unclassified duplication in normative content shall be treated as a quality issue.

## 10. Downstream document obligations [SEC:UDQ-GOV-STD-002::10]

Subsystem specifications, UI specifications, templates, and reports shall:

- use glossary-owned meanings consistently,
- reference the owning term or document where helpful,
- avoid shadow definitions,
- avoid treating examples as alternative definitions,
- update the contradiction or duplication register when drift is discovered.
