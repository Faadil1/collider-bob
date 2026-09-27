# Fresh-Agent Replay — Attempt 01 — 2026-09-27

Status: **REPLAY_FAIL**  
Execution source: **LIVE_BOB_SESSION**  
Bob task id: `4100558a9ec3bb56296149a8388af980`

## Experimental setup

The fresh Bob task ran in a physically isolated workspace constructed from:

- base implementation commit: `8370a82861cd27eb972700f74c916743e3fa578b`;
- stale API implementation: `customer_identity=email`;
- authoritative INTERACTIVE decision memory and patched specification;
- no repaired implementation from the prior LIVE_BOB decision run;
- no prior `repair.patch`;
- no test suite;
- no regression contract during agent execution;
- MCP disabled;
- subagents disabled.

Replay input bundle SHA-256:

`a3a13447d5392d7369fd5432078e3fc11cedd4fb3b114df93b662458f46e9a26`

## Observed Bob result

The fresh Bob task independently read the authoritative workspace evidence and emitted:

- concept: `customer_identity`;
- emitted value: `account_id`;
- epistemic state: `OBSERVED`;
- changed file: `api/handlers/recover.py`.

This establishes **semantic convergence** on the human-approved canon.

Bob task runtime metadata:

- session/task ref: `bob-task:4100558a9ec3bb56296149a8388af980`;
- agent id: `bob-headless-agent:4100558a9ec3bb56296149a8388af980`;
- reported session cost: `0.130096`;
- duration: `24601 ms`;
- tool calls: `6`.

## Withheld regression result

After Bob finished, the previously withheld canonical regression contract was injected and executed once.

Observed result:

- **5 passed**
- **2 failed**
- exit code: `1`

Both failures were caused by the same compatibility regression. Bob changed the API to use
`account_id`, but also removed the existing `customer_email` parameter. The holdout contract expected the
public API shape to remain compatible: an email-only call should be rejected semantically with `ValueError`,
and a call containing both identity inputs should remain valid while the canonical `account_id` wins.
Because the parameter had been removed, both cases raised `TypeError`.

Classification: **API_COMPATIBILITY_REGRESSION**.

## Deterministic COLLIDER verdict

```json
{
  "status": "REPLAY_FAIL",
  "runtime_state": "LIVE_BOB_SESSION",
  "accepted": false,
  "reasons": [
    "emitted_value='account_id', tests_passed=False"
  ]
}
```

This is intentionally preserved as a failure. It is not rewritten, relabeled, or excluded.

## Evidence hashes

| Artifact | SHA-256 |
|---|---|
| input-bundle.json | `3f39f7f6a8dccc9c09ad964743be64d32e68c21349bb259135c2b8ef4a0f1fdd` |
| bob-transcript.ndjson | `c7b4c028718c36da5f1b99e3c3fb7b4e3ea9236f8e76a5302a189026be8a26ca` |
| fresh-agent-api.diff | `72d008aae9b2afb94260fa316939b52e0cfc98c489e517de5d62911658bb1bb3` |
| holdout-test.txt | `161b4b78000639f921e6e9515fbd65efc9745ca66f24061d957673ffb06a0603` |
| replay-result.json | `ea8a0add587ec6479aaf1ed0a71284f5abc385d550273a8f514c7bdf55f1cd06` |
| replay-receipt.json | `17d55906a9b4971e35f6077a5b26c181a33c553b83bfca53a2672e0003cb64b5` |

## Truth boundary

Attempt 01 proves that a fresh independent Bob task derived the correct canonical value from decision memory
and the patched specification. It **does not** prove successful implementation replay because the withheld
regression contract failed.

`FRESH-AGENT REPLAY → PROVEN` therefore remains **false**.

## Tooling defect discovered during evaluation

The CLI entry point in `collider/replay.py` attempted to use `argparse`, `json`, and `Path` without
module-level imports. The deterministic evaluation function itself worked and produced the receipt above when
called directly. The CLI import defect is a separate implementation bug and is fixed in the same follow-up
change without altering Attempt 01 evidence.
