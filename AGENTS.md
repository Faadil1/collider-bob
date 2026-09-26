# AGENTS.md — COLLIDER

## Mission
Build and prove COLLIDER: disagreement-driven specification repair for parallel AI coding agents.

## Operating rule
Agents are not read-only by default. They may create, edit, run, test, and repair within the project workstream. Execution restrictions must come from a real risk boundary, not convenience.

## Epistemic contract
Allowed labels: OBSERVED, INFERRED, UNKNOWN, AGENT_DRIFT, SPEC_GAP.
Never promote an inference into a fact. If evidence is insufficient or conflicting, return UNKNOWN or request minimal clarification.

## Canonical workflow
RUBRIC → PAIN → PROBLEM → DIFFERENTIATOR → EXECUTION → EVIDENCE → STORY → DEMO → Q&A

Macro lifecycle:
QUALIFY → DECIDE → DESIGN → DELIVER → AUDIT → EXPAND

## Mandatory gates
Eligibility/Scope/Rubric Fit; Real Problem/User; Real Negative Event; Competitive Novelty/Kill Test; Technical Reality Check; Truth Boundary/Negative Path; Security/Dependencies/Rights/Data Use; Conditional Gateway Registry; Runtime/Commit Binding; Evidence Integrity; Reproducibility/Observability; Deterministic Demo; Judge Performance Assurance; Submission Integrity; Final Snapshot/CURRENT/HANDOVER/Post-mortem.

## Failure rule
Real failure > fake success. Preserve failures, invalid assumptions, blocked paths, stale evidence, and incomplete implementation.

## Proof rule
Claim → Demonstration → Receipt.

## Current mechanism
Bob Plan decomposes work → independent subagents expose interpretations → COLLIDER classifies disagreement → explicit contradiction becomes AGENT_DRIFT; unresolved ambiguity becomes SPEC_GAP / UNKNOWN → minimal clarification → canon patch → only dependent workstreams are replanned/repaired.