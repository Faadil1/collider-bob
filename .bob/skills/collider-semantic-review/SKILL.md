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

## Live Bob protocol

Follow `LIVE-RUN-PROTOCOL.md` exactly.

For the canonical failed-payment scenario:

1. Read `fixtures/failed-payment/BRIEF.md`.
2. Spawn three independent Bob subagents in parallel:
   - API
   - Ledger
   - Notifications
3. Give each subagent the same authoritative brief plus only the files for its
   assigned workstream. Do not reveal sibling interpretations.
4. Require each subagent to return one JSON interpretation object following
   `INTERPRETATION-TEMPLATE.json` and
   `schemas/interpretation.schema.json`.
5. In the parent Bob session, save the three returned objects to:
   `.collider/bob-live/<run-id>/interpretations/{api,ledger,notifications}.json`
6. Ensure each object records:
   - `generation_mode: LIVE_BOB`
   - the same real `session_ref`
   - a real `task_summary_ref`
   - a unique `agent_id`
7. Validate before COLLIDER is allowed to consume them:

   ```bash
   python3 -m collider.bob_live validate \
     --interpretations-dir .collider/bob-live/<run-id>/interpretations \
     --session-ref "<real-bob-session-ref>" \
     --receipt .collider/bob-live/<run-id>/bob-live-input.json
   ```

8. Run COLLIDER against the live Bob interpretations, first without a human
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

9. If COLLIDER returns a SPEC_GAP, ask the human exactly the minimal question.
   Do not choose for them.

10. After the human answers, rerun to a new immutable transient run directory
    with `--human-decision ... --human-decision-source INTERACTIVE`.

11. When decision memory exists in the compiled workspace, export it into Bob
    workspace rules:

    ```bash
    python3 -m collider.bob_rules \
      --memory <compiled-workspace>/canon/decision-memory.json \
      --output .bob/rules/collider-decision-memory.md
    ```

12. Run the COLLIDER guard. Show the three possible outcomes:
    `MERGE_ALLOWED`, `MERGE_BLOCKED`, `DECISION_REQUIRED`.

## Evidence capture

After the live run, capture the Bob Task Session Summary and the parallel
subagent panel. Save only authentic screenshots under `evidence/bob-sessions/`.

Do not create placeholder screenshots and do not convert PRESEEDED evidence into
a LIVE_BOB claim.
