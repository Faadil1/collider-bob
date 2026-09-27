# IBM Bob Usage Statement

IBM Bob 2.0 was used as a load-bearing development agent during the implementation,
hardening, and live proof of COLLIDER.

Bob worked directly inside the project repository in GitHub Codespaces. COLLIDER
ships a Bob-native integration layer: a custom Semantic CI mode, reusable semantic
review skill, workspace truth/decision-memory rules, project MCP server, lifecycle
hooks, LIVE_BOB provenance validator, and decision-memory exporter.

## Observed LIVE_BOB run

A real Bob session executed the canonical ambiguity protocol as
`live-bob-2026-09-27-01`.

Before the three probes ran, the existing `customer_identity` decision-memory rule
was quarantined and SHA-256 recorded so it could not leak the known answer into the
independent probes. Three isolated Bob subagents then interpreted API, Ledger, and
Notifications separately. None cited the quarantined canon. The rule was restored
byte-for-byte and its SHA-256 reverified before classification.

The resulting bundle passed COLLIDER's LIVE_BOB provenance validator with three
unique agents and real session/task references. Before any human answer,
COLLIDER classified `customer_identity` as `SPEC_GAP / UNKNOWN`: API chose
`email`, Ledger chose `account_id`, and the source was silent. Bob stopped on
the minimum human clarification instead of inventing an answer.

The user then selected `account_id` interactively. COLLIDER recorded
`human_decision_source=INTERACTIVE`, compiled the decision, exported Bob decision
memory, repaired the resolved path, reached zero integration conflicts, passed the
30 workstream tests, and produced `MERGE_ALLOWED` on the PR semantic gate.

## Fresh-agent replay

The replay proof deliberately preserved failures instead of retrying invisibly.

**Attempt 01** ran a new headless Bob task in a physically isolated workspace with
the stale implementation, authoritative INTERACTIVE decision memory/specification,
no repaired implementation, no prior `repair.patch`, no MCP, no subagents, and no
tests or regression contract visible during execution.

The fresh task correctly derived `account_id`, but over-repaired the API by
removing the existing `customer_email` parameter. When the previously withheld
canonical contract was revealed afterward, the result was **5 passed / 2 failed**.
COLLIDER recorded `REPLAY_FAIL`. That attempt remains immutable evidence.

**Attempt 02** started from a new isolated sandbox and did not receive Attempt 01's
implementation, failure details, prior outputs, tests, or hidden contract. The only
added instruction was a general engineering constraint: make the narrowest
authoritative change and preserve existing public signatures/unrelated behavior
unless the sources require a breaking change.

Bob again derived `account_id`, preserved the public API signature, and changed
the stale API behavior. Only after Bob finished was the same canonical regression
contract generated and revealed. It passed **7/7**, and COLLIDER deterministically
returned:

```text
REPLAY_PASS
runtime_state: LIVE_BOB_SESSION
accepted: true
```

This is therefore claimed precisely as a **targeted fresh-agent repair replay**,
not an unconstrained first-try replay.

## Provenance boundary

The older comparative fixture interpretations remain **PRESEEDED**. They are not
relabeled as Bob output. The observed LIVE_BOB run and both replay attempts are
separate, session-bound evidence.

The three future guard probes are controlled edits, not autonomous agents. No
unmeasured time-saving or percentage-productivity claim is made.

Canonical evidence:

- `evidence/bob-sessions/LIVE-BOB-2026-09-27-01.md`
- `evidence/bob-sessions/FRESH-REPLAY-ATTEMPT-01-2026-09-27.md`
- `evidence/bob-sessions/FRESH-REPLAY-ATTEMPT-02-2026-09-27.md`
- `evidence/bob-sessions/JUDGE-EVIDENCE-MANIFEST-2026-09-27.md`

COLLIDER applies its own standard to its IBM Bob claims: **real failure > fake
success**.
