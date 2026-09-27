---
name: collider-semantic-review
description: Run COLLIDER Semantic CI with isolated Bob subagents to expose specification gaps, classify agent drift, compile human decisions, and guard future changes.
---

# COLLIDER Semantic Review

Use this skill when multiple implementations, agents, or workstreams may be
locally valid but semantically incompatible.

## Non-negotiable truth rules

- Never upgrade agreement into fact without source authority.
- Never label an interpretation `LIVE_BOB` unless it was produced in this real
  Bob session by a Bob subagent.
- Never call controlled guard probes "agents".
- Preserve `UNKNOWN` when the source is silent.
- Do not rewrite committed evidence. Use `.collider/` for transient live runs.
- A live Bob interpretation run and a fresh-agent replay are different proofs.

## Native Bob entry sequence

Before the live protocol:

1. Use the project MCP tool `collider_decision_memory` to load current canon.
2. Use `collider_gate` to inspect the current semantic state.
3. Confirm the session-start hook injected a real Bob `session_id` and wrote a
   transient receipt under `.collider/bob-hooks/`.
4. Keep the MCP server, lifecycle hooks, and this skill active for the run.

The MCP tools are part of the product surface. CLI commands below are fallback
and evidence-friendly equivalents, not the preferred Bob interaction path.

## Live Bob protocol

Follow `LIVE-RUN-PROTOCOL.md` exactly.

For the canonical failed-payment scenario:

1. Briefly switch to Bob **Plan** mode and produce only a workstream-decomposition
   artifact at `.collider/bob-live/<run-id>/plan.md`. Plan may define scopes,
   inputs and isolation boundaries, but must not choose ambiguous semantic
   values. Return to `collider-semantic-ci` mode after the plan is accepted.

2. Read `fixtures/failed-payment/BRIEF.md`.
3. Spawn three independent **general** Bob subagents in parallel:
   - API
   - Ledger
   - Notifications

   Keep `fork_context: false` for all three. Their isolated context windows are
   the ambiguity-probe mechanism, not a token-saving convenience.

4. Give each subagent the same authoritative brief plus only the files for its
   assigned workstream. Do not reveal sibling interpretations, summaries, or
   chosen values until all three have returned.
5. Require each subagent to return one JSON interpretation object following
   `INTERPRETATION-TEMPLATE.json` and
   `schemas/interpretation.schema.json`.
6. In the parent Bob session, save the three returned objects to:
   `.collider/bob-live/<run-id>/interpretations/{api,ledger,notifications}.json`
7. Ensure each object records:
   - `generation_mode: LIVE_BOB`
   - the same real `session_ref`
   - a real `task_summary_ref`
   - a unique `agent_id`
8. Validate before COLLIDER is allowed to consume them. Prefer the native MCP
   tool `collider_validate_live_bob`. For a terminal receipt, run:

   ```bash
   python3 -m collider.bob_live validate \
     --interpretations-dir .collider/bob-live/<run-id>/interpretations \
     --session-ref "<real-bob-session-ref>" \
     --receipt .collider/bob-live/<run-id>/bob-live-input.json
   ```

9. Run COLLIDER against the live Bob interpretations, first without a human
   decision:

   ```bash
   python3 -m collider.pipeline \
     --run-id <run-id>-detect \
     --run-dir .collider/bob-live/<run-id>/detect \
     --interpretation-dir .collider/bob-live/<run-id>/interpretations \
     --execution-environment LIVE_BOB_SESSION \
     --interpretation-source LIVE_BOB \
     --bob-session-ref "<real-bob-session-ref>"
   ```

10. If COLLIDER returns a SPEC_GAP, ask the human exactly the minimal question.
   Do not choose for them.

11. After the human answers, compile that decision **from the same validated
    LIVE_BOB interpretation bundle**. Prefer the approval-gated native MCP tool
    `collider_compile_live_decision`. Do not fall back to PRESEEDED fixtures.
    CLI equivalent:

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

    The compiler must persist the validated LIVE_BOB bundle hash into decision
    memory and the decision receipt.

12. Export the compiled decision memory into Bob workspace rules. Prefer the
    approval-gated MCP tool `collider_export_decision_rule`; CLI equivalent:

    ```bash
    python3 -m collider.bob_rules \
      --memory <compiled-workspace>/canon/decision-memory.json \
      --output .bob/rules/collider-decision-memory.md
    ```

13. Run the COLLIDER guard. Show the three possible outcomes:
    `MERGE_ALLOWED`, `MERGE_BLOCKED`, `DECISION_REQUIRED`.

14. For fresh-agent proof, start a new independent Bob `general` subagent with
    repaired implementation withheld. Evaluate its real result with
    `collider_evaluate_replay`. Never infer replay success from the original
    session.

15. Let the Bob `Stop` lifecycle hook write the final session/gate receipt.
    This receipt proves session lifecycle + semantic state only; the subagent
    interpretation bundle remains the source for LIVE_BOB provenance.

## Evidence capture

After the live run, capture the Bob Task Session Summary and the parallel
subagent panel. Save only authentic screenshots under `evidence/bob-sessions/`.

Do not create placeholder screenshots and do not convert PRESEEDED evidence into
a LIVE_BOB claim.
