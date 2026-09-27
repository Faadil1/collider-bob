# Fresh-Agent Replay — Attempt 02 — 2026-09-27

Status: **REPLAY_PASS**  
Attempt type: **TARGETED_REPAIR_REPLAY**  
Execution source: **LIVE_BOB_SESSION**  
Bob task id: `9a6ec967e19713910d16b99184b15307`

## Why Attempt 02 exists

Attempt 01 is preserved as an authentic `REPLAY_FAIL`: Bob correctly derived
`account_id`, but removed the existing `customer_email` parameter and failed
2 of 7 withheld compatibility checks.

Attempt 02 started from a brand-new isolated sandbox. It did **not** receive:

- Attempt 01's implementation;
- Attempt 01's failure details;
- any prior `repair.patch`;
- any prior replay output;
- the regression contract;
- tests.

The only added engineering constraint was general rather than holdout-specific:

> Apply the narrowest change required by the authoritative decision. Preserve
> existing public function signatures and unrelated behavior unless the
> authoritative sources explicitly require a breaking interface change.

This makes Attempt 02 a **targeted-repair replay**, not an unconstrained replay.

## Observed Bob execution

Bob read the authoritative INTERACTIVE decision memory and patched specification,
derived `customer_identity = account_id`, and changed only
`api/handlers/recover.py`.

The public function signature retained both optional identity parameters while the
live path switched to `customer_account_id`.

Observed result:

- emitted value: `account_id`
- epistemic state: `OBSERVED`
- Bob task id: `9a6ec967e19713910d16b99184b15307`
- session/task ref: `bob-task:9a6ec967e19713910d16b99184b15307`
- reported session cost: `0.20998`
- duration: `25756 ms`
- tool calls: `8`

Replay input SHA-256 reported in the result:

`27d48a346c7801ba2f2d4e18157c2fa1ef36508f07370ca83839fde915a8b1b2`

## Holdout revelation

Bob completed before the canonical regression contract was created in the strict
agent workspace.

The holdout was then generated from COLLIDER's own `contract_source()`:

- contract SHA-256: `df25451d2298d74d22251b92d6ac855b03b377ea4dc85e950c8073caaa15fcae`
- observed result: **7 passed, 0 failed**
- exit code: `0`

## Deterministic COLLIDER verdict

```json
{
  "status": "REPLAY_PASS",
  "runtime_state": "LIVE_BOB_SESSION",
  "accepted": true,
  "reasons": []
}
```

Therefore the current truth is:

- LIVE_BOB ambiguity proof: **OBSERVED**
- human decision: **INTERACTIVE**
- fresh-agent Attempt 01: **REPLAY_FAIL**
- targeted fresh-agent Attempt 02: **REPLAY_PASS**
- targeted replay proof: **PROVEN**

## Evidence hashes

| Artifact | SHA-256 |
|---|---|
| input-bundle.json | `42ab6d497bb4ca3586e98cf68e222ce2708df9664bbcf0237297f1c79dc6f181` |
| bob-transcript.ndjson | `d082a63321aea01c525ad35dba05eb7b8380423996fdc79793850077c67affb4` |
| fresh-agent-api.diff | `aee0f46a130f1a62b5132105b61153c5d19910415caf5ea7ead4b7119a7dacb8` |
| holdout-test.txt | `ee09f6debd9f81709cd5af75a47e8b1c6ed9a94b8e82a9b34c00f597199e9c17` |
| replay-result.json | `aa10c185b3bee095b8680c7e021953f103226493774147519d2139988e67e056` |
| replay-receipt.json | `ed623331edefb259ffc7047a98f3091fd0a0ac0d94566c927c4d4f9da71a12c0` |

## Raw receipt caveat

The raw `replay-receipt.json` embeds the original replay request scaffold, which
still contains stale historical text saying the Bob budget was exhausted and the
runtime was pending. That request metadata predates the real live execution.

It is preserved as raw history and must not be used to characterize Attempt 02.
The actual execution truth is established by the Bob transcript/task id, result
object, holdout output, hashes, and deterministic verdict above.

## Screenshot pool

Original Bob screenshots from the live proof and replay workflow remain part of the
working evidence pool. They should be archived without reconstruction and curated
later into a smaller judge-facing set.
