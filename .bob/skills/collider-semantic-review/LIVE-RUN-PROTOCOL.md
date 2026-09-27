# Live Bob Run Protocol

This protocol turns Bob from a build-time assistant into a provenance-bearing
runtime input for COLLIDER.

## 1. Session identity

Before spawning subagents, choose a run id and record the real Bob task/session
reference visible in Bob.

```text
run-id: live-bob-2026-09-27-01
session-ref: <copy from Bob task/session UI>
```

Do not invent a session reference.

## 2. Plan decomposition

Use Bob Plan mode to create a bounded decomposition artifact for API, Ledger,
and Notifications at `.collider/bob-live/<run-id>/plan.md`.

The plan may define scopes, inputs and isolation boundaries. It must **not**
choose source-silent semantic values. This keeps planning useful without letting
the planner contaminate the independent ambiguity probes.

Return to COLLIDER Semantic CI mode before execution.

## 3. Decision-memory quarantine

The canonical demo workspace already contains a Bob decision-memory rule for
`customer_identity=account_id`. Workspace rules apply across modes, so leaving
that rule active during a fresh ambiguity probe would leak the answer.

Before spawning the interpretation subagents:

1. Create `.collider/bob-live/<run-id>/quarantine/`.
2. Compute and record the SHA-256 of
   `.bob/rules/collider-decision-memory.md`.
3. Move that rule into the transient quarantine directory without modifying bytes.
4. Confirm the original rule path is absent.
5. Do not pass the parent's remembered canonical value into any subagent prompt.

After all three independent interpretations return, but before DETECT or a human
decision:

1. Restore the rule to its original path.
2. Verify its SHA-256 exactly matches the pre-probe hash.
3. If restoration/hash verification fails, stop the run.
4. If any subagent cites the quarantined rule or existing canon as evidence,
   mark the probe contaminated and rerun it.

Quarantine is a bounded experimental control, not deletion of memory. GUARD and
fresh replay run with decision memory restored.

## 4. Isolation contract

Spawn API, Ledger, and Notifications as separate Bob `general` subagents with
`fork_context: false`.

Each receives:

- the authoritative brief;
- only its assigned workstream files;
- the interpretation schema/template;
- no sibling interpretation;
- no canonical answer.

The parent may know all three tasks. The subagents must not know each other's
choices before returning their own interpretation.

## 5. Output contract

Each subagent returns a JSON object with:

- unique `agent_id`;
- matching `workstream`;
- `generation_mode: LIVE_BOB`;
- the real parent `session_ref`;
- a real `task_summary_ref`;
- claims with source evidence and artifact references.

An OBSERVED claim must cite source evidence. An INFERRED claim must not be
promoted because other agents agree. UNKNOWN is valid.

## 6. Validation

The parent writes the three objects to the transient live directory and validates
them with the native MCP tool `collider_validate_live_bob` or:

```bash
python3 -m collider.bob_live validate \
  --interpretations-dir .collider/bob-live/<run-id>/interpretations \
  --session-ref "<real-bob-session-ref>" \
  --receipt .collider/bob-live/<run-id>/bob-live-input.json
```

If validation fails, repair metadata or rerun the affected subagent. Never bypass
validation.

## 7. Detect before decide

Run COLLIDER on the validated LIVE_BOB bundle with no human decision first.
Preserve the immutable detection receipt.

If a SPEC_GAP appears, surface only the minimal question to the human.

## 8. Compile the human decision

Compile the human answer from the **same validated LIVE_BOB bundle**:

```bash
python3 -m collider.decision_compiler \
  --concept customer_identity \
  --value "<human-answer>" \
  --decision-id <run-id>-decision \
  --human-decision-source INTERACTIVE_BOB \
  --interpretation-source LIVE_BOB \
  --interpretation-dir .collider/bob-live/<run-id>/interpretations \
  --bob-session-ref "<real-bob-session-ref>" \
  --out-dir .collider/bob-live/<run-id>/decision \
  --workspace .collider/bob-live/<run-id>/workspace
```

The compiler must copy the exact live interpretations into its workspace and
persist the Bob session reference plus LIVE_BOB bundle SHA-256 into decision
memory and the decision receipt.

Never label a prefilled answer interactive. Never fall back to PRESEEDED
interpretations after a live human clarification.

## 9. Persist the decision into Bob

Export the compiled decision memory into
`.bob/rules/collider-decision-memory.md`, preferably through the approval-gated
MCP tool `collider_export_decision_rule` (CLI equivalent:
`python3 -m collider.bob_rules`).

This makes approved semantic canon available to future Bob sessions. Rule export
alone does not prove a future agent obeyed it.

## 10. Guard

Run COLLIDER's guard and expose all three possible product verdicts:
`MERGE_ALLOWED`, `MERGE_BLOCKED`, `DECISION_REQUIRED`.

## 11. Fresh-agent replay

Start a **new independent Bob `general` subagent** against the patched
specification and restored decision rule while withholding repaired code,
`repair.patch`, and the canonical answer in the prompt.

Only actual `LIVE_BOB_SESSION` replay evidence may be accepted by
`collider_evaluate_replay` / `collider.replay`.

## 12. Capture

Capture authentic evidence:

- parent Task Session Summary;
- Plan artifact/session evidence;
- parallel subagent panel;
- one subagent summary per workstream;
- LIVE_BOB validation receipt;
- decision compilation/verification result;
- final guard verdict;
- fresh replay summary if executed.

Store authentic captures under `evidence/bob-sessions/`.
