# Live Bob Run Protocol

This protocol turns Bob from a build-time assistant into a provenance-bearing
runtime input for COLLIDER.

## 1. Session identity

Before spawning subagents, choose a run id and record the real Bob task/session
reference visible in Bob.

Example:

```text
run-id: live-bob-2026-09-27-01
session-ref: <copy from Bob task/session UI>
```

Do not invent a session reference.

## 2. Isolation contract

Spawn API, Ledger, and Notifications as separate Bob subagents.

Each receives:

- the authoritative brief;
- only its assigned workstream files;
- the interpretation schema/template;
- no sibling interpretation;
- no canonical answer.

The parent may know all three tasks. The subagents must not know each other's
choices before returning their own interpretation.

## 3. Output contract

Each subagent returns a JSON object with:

- unique `agent_id`;
- matching `workstream`;
- `generation_mode: LIVE_BOB`;
- the real parent `session_ref`;
- a real `task_summary_ref`;
- claims with source evidence and artifact references.

An OBSERVED claim must cite source evidence. An INFERRED claim must not be
promoted because other agents agree. UNKNOWN is valid.

## 4. Validation

The parent writes the three objects to the transient live directory and runs
`python3 -m collider.bob_live validate`.

If validation fails, repair the evidence metadata or rerun the affected
subagent. Do not bypass validation.

## 5. Detect before decide

Run COLLIDER without a human decision first. Preserve that receipt.

If a SPEC_GAP appears, surface the minimal question to the human.

## 6. Compile the human decision

Run a second immutable live directory with the human answer explicitly marked
`INTERACTIVE`.

Never label a prefilled answer as interactive.

## 7. Persist the decision into Bob

Export COLLIDER decision memory to `.bob/rules/collider-decision-memory.md`.
This makes the approved semantic decision part of Bob's workspace rules for
future sessions.

This rule export is a product behavior. It is not evidence that a future agent
obeyed the rule until such an agent is actually run.

## 8. Fresh-agent replay

A fresh-agent replay is a separate proof. Start a new independent Bob agent with
the patched specification and decision rule, while withholding repaired code.
Only then may `collider.replay` accept `LIVE_BOB_SESSION` evidence.

## 9. Capture

Capture:
- parent task/session summary;
- parallel subagent panel;
- one subagent summary per workstream;
- the terminal validation receipt;
- the final COLLIDER verdict.

Store authentic captures under `evidence/bob-sessions/`.
