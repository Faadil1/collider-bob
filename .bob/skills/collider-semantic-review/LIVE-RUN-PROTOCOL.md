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

## 2. Decision-memory quarantine

The canonical demo workspace already contains a Bob decision-memory rule for
`customer_identity=account_id`. IBM Bob workspace rules apply across modes, so
leaving that rule active during a fresh ambiguity probe would leak the answer the
probe is supposed to derive independently.

Before spawning the three interpretation subagents:

1. Create `.collider/bob-live/<run-id>/quarantine/`.
2. Compute and record the SHA-256 of
   `.bob/rules/collider-decision-memory.md`.
3. Move that rule into the transient quarantine directory without modifying its
   bytes.
4. Confirm `.bob/rules/collider-decision-memory.md` is absent.
5. Do not pass the parent agent's remembered canonical value into any subagent
   prompt.

Only then spawn the probe subagents with `fork_context: false`.

After all three independent interpretations have returned, but before DETECT or
any human decision:

1. Restore the quarantined rule to its original path.
2. Verify its SHA-256 exactly matches the pre-probe hash.
3. If restoration or hash verification fails, stop the run.
4. If any subagent cites the quarantined rule or an existing canonical decision as
   evidence, mark the probe contaminated and rerun it.

The quarantine is not deletion of decision memory. It is a bounded experimental
control used only while generating independent ambiguity probes. GUARD and fresh
replay run with decision memory restored.

## 3. Isolation contract

Spawn API, Ledger, and Notifications as separate Bob subagents.

Each receives:

- the authoritative brief;
- only its assigned workstream files;
- the interpretation schema/template;
- no sibling interpretation;
- no canonical answer.

The parent may know all three tasks. The subagents must not know each other's
choices before returning their own interpretation.

## 4. Output contract

Each subagent returns a JSON object with:

- unique `agent_id`;
- matching `workstream`;
- `generation_mode: LIVE_BOB`;
- the real parent `session_ref`;
- a real `task_summary_ref`;
- claims with source evidence and artifact references.

An OBSERVED claim must cite source evidence. An INFERRED claim must not be
promoted because other agents agree. UNKNOWN is valid.

## 5. Validation

The parent writes the three objects to the transient live directory and runs
`python3 -m collider.bob_live validate`.

If validation fails, repair the evidence metadata or rerun the affected
subagent. Do not bypass validation.

## 6. Detect before decide

Run COLLIDER without a human decision first. Preserve that receipt.

If a SPEC_GAP appears, surface the minimal question to the human.

## 7. Compile the human decision

Run a second immutable live directory with the human answer explicitly marked
`INTERACTIVE`.

Never label a prefilled answer as interactive.

## 8. Persist the decision into Bob

Export COLLIDER decision memory to `.bob/rules/collider-decision-memory.md`.
This makes the approved semantic decision part of Bob's workspace rules for
future sessions.

This rule export is a product behavior. It is not evidence that a future agent
obeyed the rule until such an agent is actually run.

## 9. Fresh-agent replay

A fresh-agent replay is a separate proof. Start a new independent Bob agent with
the patched specification and decision rule, while withholding repaired code.
Only then may `collider.replay` accept `LIVE_BOB_SESSION` evidence.

## 10. Capture

Capture:
- parent task/session summary;
- parallel subagent panel;
- one subagent summary per workstream;
- the terminal validation receipt;
- the final COLLIDER verdict.

Store authentic captures under `evidence/bob-sessions/`.
