# COLLIDER — Bob-Native Integration

**Status:** NATIVE INTEGRATION SHIPPED / LIVE SESSION PROOF PENDING.

The project now contains a real IBM Bob custom mode, reusable skill, workspace
truth rules, a LIVE_BOB provenance validator, and decision-memory → Bob-rule
export. These mechanisms are verified in the repository test suite.

What remains pending is **session evidence**: no interpretation artifact becomes
LIVE_BOB until an actual Bob task/session and subagent summaries are captured and
pass `collider.bob_live`.

## The question

> "If Bob were replaced by a generic single coding assistant, what capability would be lost?"

The designed answer: the core loop of COLLIDER cannot be constructed from a single-context
assistant at all — because the independence guarantee and targeted repair require capabilities
that a single-context assistant does not provide. This is the architectural claim. It remains
**INFERRED** until a real Bob session produces the required evidence artifacts.

---

## Capability map

### Plan mode — workstream decomposition with explicit interpretation boundaries

**What it does:** Bob Plan decomposes the brief into independent workstreams with explicit
scope boundaries. Each workstream gets a task definition that is isolated from the others.
No shared context. No coordination signals. The decomposition is the product of a planning
step, not a side effect of sequential execution.

**Why it is load-bearing:** COLLIDER's core claim is that *independent* agents, given the
same underspecified brief, will make *incompatible but locally plausible* interpretations.
This requires genuine independence at decomposition time, not simulated independence.

If Bob Plan were replaced by a human manually writing three prompts, the independence would
be engineered by hand and would depend entirely on the human's discipline in not cross-
contaminating the prompts. The system would lose the property that the decomposition itself
is a traceable, auditable artifact.

A generic single assistant cannot decompose a task into genuinely independent parallel
workstreams. It can describe what such workstreams might look like, but it cannot execute
them as independent agents.

---

### Agent mode — workstream execution with full repository capability

**What it does:** Each workstream runs as a Bob Agent subagent that can create files,
edit files, run tests, read repository context, and repair its own output within its
workstream scope.

**Why it is load-bearing:** The structured interpretation objects that COLLIDER classifies
are not answers to survey questions — they are the side effects of real implementation
decisions made by agents building real code. The `field_name: "credit_amount"` disagreement
is not a stated preference; it is what Ledger's agent actually named the field when it
implemented the ledger record. The evidence is executable.

A generic single assistant in a single context window can produce a description of three
workstreams. It cannot execute them as agents that produce independently verifiable artifacts.
If the "interpretations" are not grounded in actual code, the COLLIDER demo is a mock-up,
not a demonstration.

---

### Parallel subagents — genuinely concurrent independent interpretations

**What it does:** Bob's parallel subagent capability allows all three workstreams to execute
concurrently. Each agent produces its interpretation independently, without observing the
others' work in progress.

**Why it is load-bearing:** The independence of interpretation is the mechanism by which
COLLIDER surfaces hidden disagreements. If workstream agents execute sequentially in the
same context, each agent can observe what the previous one decided. The second and third
agents may conform to the first agent's interpretation, suppressing the disagreement that
COLLIDER needs to classify.

Concurrency is not just a performance optimization here. It is an architectural isolation
guarantee. Without it, COLLIDER would need to artificially blind sequential agents from each
other's outputs — which is possible but fragile and harder to verify.

A generic single assistant executes sequentially in one context. It cannot guarantee that
the "third workstream" has not been influenced by the first two.

---

### Repository context — source evidence lookup during classification

**What it does:** Bob agents can read repository files during execution. The classifier uses
this capability to retrieve source evidence — the brief text, spec documents, ADRs — and
locate the passage that either confirms or contradicts a workstream's interpretation.

**Why it is load-bearing:** The AGENT_DRIFT / SPEC_GAP distinction depends entirely on
whether the source material explicitly decides the question. This is not a lookup in the
agent's training data; it is a lookup in the specific documents that constitute the
specification for this project. The classifier must be able to retrieve and cite the exact
passage, at a specific location in a specific document, that was in scope when the agents
were running.

Without repository context, the classifier is operating on the agent's interpreted memory of
the brief, which is not auditable and not binding. The evidence reference that makes a
classification auditable requires access to the actual source document.

A generic single assistant with the brief in its context window has a version of this
capability, but only for content explicitly included in the conversation. It cannot retrieve
from a repository, cannot cite line numbers, and cannot guarantee that the evidence it
references is the same version the agents saw.

---

### Document understanding — reading the product brief and spec documents as evidence sources

**What it does:** Bob agents read and interpret documents in the repository — product briefs,
architecture decision records, API specs — as inputs to their implementation decisions and
as sources for the classifier's evidence lookup.

**Why it is load-bearing:** The classification of `field_name` as `AGENT_DRIFT` depends on
the classifier reading the brief and finding the word "refund_amount" as the explicitly
specified term. This is a document reading act, not a code analysis act. The brief is the
authoritative source. The classifier's authority to call `AGENT_DRIFT` comes from its ability
to point at the source document and show the contradiction.

Without document understanding as a first-class capability (not just prompt injection), the
classifier cannot distinguish between "the source said X" and "the source probably said X."
That distinction is the foundation of COLLIDER's truth boundary.

---

### Targeted repair — only rerun affected workstreams after canon patch

**What it does:** After the canon patch is written, the impact router identifies which
workstreams consumed the resolved concept. Bob's agent architecture allows COLLIDER to
rerun only those workstreams, leaving unaffected workstreams untouched.

**Why it is load-bearing:** The property being demonstrated is *minimal intervention*. The
claim is: "One question repairs only what actually depended on it." If rerunning required
rerunning all workstreams, the claim would be false. If targeted rerun is not possible,
the canon patch reduces to "restart from scratch with better context."

Targeted repair is only possible when workstreams are independent, addressable agents that
can be reinvoked with a specific context injection (the canon patch). A generic single
assistant, which builds all workstreams in one context, cannot rerun one without rerunning
the others — the context is not partitioned.

---

## Substitution test

| Bob capability | Generic single assistant substitute | What breaks |
|---------------|-------------------------------------|-------------|
| Plan mode | Human writes three isolated prompts | Decomposition is not traceable; independence depends on human discipline |
| Agent mode | Assistant describes what code might look like | Interpretations are not grounded in executable artifacts |
| Parallel subagents | Sequential runs with blinded context | Fragile; hard to verify; likely to suppress disagreements through context contamination |
| Repository context | Paste brief into conversation | Cannot cite line numbers; no version binding; not auditable |
| Document understanding | Rely on assistant's memory of pasted text | "Source said X" becomes "I believe the source said X" — not auditable |
| Targeted repair | Re-run everything | Loses the minimal-intervention property; demo claim becomes false |

---

## Summary

**Epistemic state: INFERRED — pending runtime proof.**

The architecture assigns Bob's specific properties — parallel independent agents, Plan mode
decomposition, repository context, targeted repair — as the mechanism by which disagreements
are surfaced, classified, and resolved with minimal intervention. Each property has a designed
load-bearing role. None of those roles is replicated by a generic single-context assistant.

This is the architectural design claim. The runtime claim — that a real Bob session confirms
each capability is actually load-bearing in the working product — is PENDING. It becomes
OBSERVED when a canonical session produces evidence artifacts that demonstrate each property.

Until then: Bob-native architecture designed; runtime proof pending.


---

## Shipped Bob-native surface — 2026-09-27

The designed architecture above is now represented by executable/project-native
integration points:

- `.bob/custom_modes.yaml` — COLLIDER Semantic CI mode with read/edit/execute,
  Skill and Subagent tool groups.
- `.bob/skills/collider-semantic-review/` — live run protocol and output
  contract for isolated API/Ledger/Notifications Bob subagents.
- `.bob/rules/collider-truth-boundary.md` — project-wide provenance and
  abstention constraints automatically injected into Bob conversations.
- `collider/bob_live.py` — validates three unique LIVE_BOB agents, one real
  parent session reference, real task-summary references, claim evidence, and
  hashes the exact interpretation bundle before COLLIDER can consume it.
- `collider.pipeline --interpretation-dir ... --interpretation-source LIVE_BOB
  --bob-session-ref ...` — the normal COLLIDER pipeline can consume validated
  Bob outputs instead of PRESEEDED fixtures.
- `collider/bob_rules.py` — turns verified decision memory into
  `.bob/rules/collider-decision-memory.md`, making approved semantic canon
  automatically available to future Bob sessions.

### Current truth state

```text
Bob custom mode / skill / rules            SHIPPED
LIVE_BOB input validation                  SHIPPED + TESTED
COLLIDER consumption of LIVE_BOB inputs    SHIPPED + TESTED
Decision memory → Bob workspace rule       SHIPPED + TESTED
Real Bob task/session execution            PENDING USER RUN
Fresh independent Bob replay               PENDING LIVE_BOB
```

The code path exists now; the remaining gate is empirical, not architectural.
A real Bob session must execute it before the corresponding runtime claims are
promoted to OBSERVED.


### Native MCP surface

IBM Bob supports project-scoped MCP configuration through `.bob/mcp.json`.
COLLIDER now ships a zero-third-party-dependency STDIO MCP server at
`collider/mcp_server.py`.

Bob discovers six structured tools:

- `collider_gate`
- `collider_pr_gate`
- `collider_decision_memory`
- `collider_validate_live_bob`
- `collider_export_decision_rule`
- `collider_evaluate_replay`

Read-only checks and provenance validation are auto-approved in project config.
Rule export and replay evaluation are deliberately not auto-approved.

The test suite launches the MCP server as a real subprocess and completes a
newline-delimited JSON-RPC initialize/tools-list round trip. This proves the
project MCP process surface itself; an actual Bob IDE connection is still
separate empirical evidence.

### Real pull-request Semantic CI surface

`.github/workflows/semantic-ci.yml` runs COLLIDER on pull requests and posts
one of the three product verdicts directly into the PR:

`MERGE_ALLOWED · MERGE_BLOCKED · DECISION_REQUIRED`

The action also executes the conventional API/Ledger/Notifications test suite
and reports its result beside the semantic verdict. This makes the core
distinction visible in the developer workflow: conventional tests can remain
green while COLLIDER still requires a missing decision.

A machine-readable semantic receipt is uploaded as a workflow artifact.


### Lifecycle-hook surface

COLLIDER now uses Bob's workspace lifecycle hooks through `.bob/settings.json`:

- `SessionStart` runs `python3 -m collider.bob_hook session-start`.
  It captures Bob's real `session_id`, current Git commit/branch, semantic-gate
  verdict and canonical decisions, writes a transient receipt under
  `.collider/bob-hooks/`, and injects concise truth-bounded context into Bob.
- `Stop` runs `python3 -m collider.bob_hook stop` and writes the final
  session/gate receipt for the same Bob session.

This makes semantic context persistent at the Bob session boundary instead of
depending on a user remembering to paste decision history.

The hook code and receipt semantics are tested. A hook receipt is explicitly
**not** treated as LIVE_BOB interpretation proof or fresh-agent replay proof.

### Bob capability stack now shipped

```text
CUSTOM MODE
  ↓
MODE-SPECIFIC + WORKSPACE RULES
  ↓
SKILL
  ↓
PARALLEL GENERAL SUBAGENTS (fork_context=false)
  ↓
PROJECT MCP TOOLS
  ↓
LIVE_BOB PROVENANCE VALIDATION
  ↓
COLLIDER PIPELINE
  ↓
DECISION MEMORY → BOB WORKSPACE RULE
  ↓
GITHUB PR SEMANTIC CI
  ↓
FRESH BOB REPLAY CONTRACT
```

The architecture now uses the native extension surfaces IBM documents for Bob:
custom modes, project skills, project rules, project MCP, custom slash commands,
parallel subagents and lifecycle hooks. The remaining gap is not another design
artifact; it is the actual Bob execution/capture that promotes runtime evidence.
