# AGENTS.md — COLLIDER

## Mission

Build and prove COLLIDER: **Semantic CI for Agentic Software Development**.

Independent implementation agents are treated as ambiguity probes. Their
disagreements can reveal specification decisions that do not yet exist.

## Operating rule

Agents are not read-only by default. They may create, edit, run, test, and repair
inside the project workstream. Execution restrictions must come from a real risk
boundary, not convenience.

## Epistemic contract

Allowed labels:

`OBSERVED · INFERRED · UNKNOWN · AGENT_DRIFT · SPEC_GAP`

Never promote inference or consensus into fact.

If evidence is insufficient or conflicting, preserve UNKNOWN or request the
minimum clarification.

## Product loop

`PROBE → COLLIDE → ADJUDICATE → DECIDE → COMPILE → PATCH → VERIFY → REMEMBER → GUARD`

Fresh-agent `REPLAY` remains a North Star step and must not be simulated as live
proof.

## Truth boundary

Canonical interpretation objects are PRESEEDED, not LIVE_BOB.

Guard probes are fixed controlled changes, not autonomous agents.

Bob was genuinely used in development; do not conflate that with the provenance
of canonical runtime interpretations.

## Proof rule

`Claim → Demonstration → Receipt`

No gate is promoted because a document says it passed. Evidence must exist.

## Canonical state

At material decisions, gates, builds, proofs, or deployments, update:

- `state/CURRENT.yaml`
- `state/HANDOVER.yaml`
- `product/GATEWAY-REGISTRY.md`

## Failure rule

**Real failure > fake success.**

Preserve meaningful failures, blocked paths, invalid assumptions, stale evidence
and explicit limitations.
