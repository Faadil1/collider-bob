# COLLIDER V2 — Spec X-Ray + Dynamic Concept Discovery

Status: BUILD BRANCH
Branch: `v2/spec-xray-dynamic-concepts`

## North Star

Turn COLLIDER from a bounded failed-payment Semantic CI proof into reusable
Bob-native infrastructure that can inspect an unfamiliar repository or brief,
discover the semantic decisions that matter, expose where source authority ends,
and compile human decisions into deterministic CI memory.

The product claim stays unchanged:

> Models may propose interpretations. Source evidence determines authority.
> Humans decide missing authority. Deterministic CI enforces the decision.

## V2 product loop

```
INGEST
  → DISCOVER
  → SPEC X-RAY
  → COLLIDE
  → ADJUDICATE
  → DECIDE
  → COMPILE
  → VERIFY
  → REMEMBER
  → GUARD
```

### INGEST

Accept a repository/working tree plus one or more authoritative requirement
sources. V2 must not assume the failed-payment fixture.

### DISCOVER

Bob subagents independently propose semantic concepts, boundaries, values and
source evidence. Discovery output is a proposal, never canon.

Required record per proposal:

- concept key + human-readable label
- workstream / file / symbol that consumes it
- observed implementation value
- exact source evidence, or explicit source silence
- epistemic state
- provenance: Bob session / task / agent

### SPEC X-RAY

Render the authoritative brief/spec with each sentence mapped to the concepts it
constrains. Concepts become visually distinguishable as:

- DECIDED — source authority exists
- UNDECIDED — plausible implementations diverge and source is silent
- ASSUMED — implementations agree but source is silent
- DRIFT — implementation contradicts explicit authority

The X-Ray is not an LLM confidence heatmap. Every state must be derivable from
evidence that can be inspected.

### DETERMINISTIC HANDOFF

Dynamic discovery ends before adjudication. Proposed concepts are normalized
into a registry snapshot, then the existing deterministic classifier applies:

- source explicit + implementation differs → AGENT_DRIFT
- source silent + implementations differ → SPEC_GAP / UNKNOWN
- source silent + implementations agree → SHARED_ASSUMPTION / INFERRED
- resolved human canon + implementation differs → MERGE_BLOCKED

## First technical correction: workspace-aware canon

V1's root gate always evaluates the committed pre-decision tree. A LIVE_BOB run
can compile a decision into a transient workspace, but a bare MCP `collider_gate`
call still targets the unchanged repository root.

V2 fixes the routing without falsifying history:

- `collider_gate(root=".")` remains the baseline gate.
- `collider_gate(root="<compiled-workspace>")` evaluates the real resolved tree.
- Bob's semantic-review skill must explicitly target the compiled workspace after
  a decision.
- No PRESEEDED artifact is relabeled INTERACTIVE or LIVE_BOB.

This makes the decision path load-bearing while preserving the original baseline.

## Packaging target

V2 should be adoptable in another Bob workspace at three levels:

1. Skill only
2. Skill + MCP
3. Full integration: Skill + Custom Mode + MCP + rules + hooks + GitHub Semantic CI

Target future UX:

```bash
collider init
collider inspect
collider gate
```

These commands are product targets, not claims about V1.

## Build order

1. Workspace-aware canon routing — ACTIVE
2. Dynamic concept proposal schema
3. Repository/brief ingestion boundary
4. Independent Bob discovery probes
5. Deterministic concept normalization + adjudication
6. Spec X-Ray data model
7. Spec X-Ray UI
8. PR decision workflow
9. Additional fixtures: timezone, idempotency, rounding, currency
10. Packaging / `collider init`
11. Spec-health telemetry

## Promotion gates

V2 is not allowed to claim arbitrary-repo support until all are PROVEN:

- unfamiliar repo can be ingested without fixture-specific code paths
- concepts are discovered rather than pre-registered
- source silence is distinguished from source evidence
- one human decision can be compiled into reusable decision memory
- a later violating change is blocked deterministically
- the same repo can be re-run without requiring the original discovery agents
- at least three non-payment fixtures pass end-to-end

## Non-goals

- LLMs do not decide truth.
- Consensus does not become authority.
- No universal "spec quality score" derived from opaque model confidence.
- No fabricated ROI or speed claims.
- No rewrite of the sealed hackathon evidence.
