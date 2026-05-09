# UniversalDAQ — Event Schema Guide

## Summary visibility policy
- Runtime events, alarm events, and operator actions are summary-eligible.
- Automation claims and diagnostic snapshots remain available but are not promoted into reviewer summaries unless a future sprint explicitly chooses to surface them.

## CSV/JSON policy
All taxonomy categories remain serializable. The new coherence layer annotates rows with source surface, owner module, category, audience, and summary visibility.
