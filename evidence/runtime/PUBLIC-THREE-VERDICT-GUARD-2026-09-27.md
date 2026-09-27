# Public Three-Verdict Guard Proof — 2026-09-27

## Scope

User-recorded production smoke on:

https://collider-semantic-ci.faadil-casecraft.workers.dev/

This receipt records only what was visibly observed in the public UI. It does not
upgrade PRESEEDED interpretations to LIVE_BOB and does not claim that the fixed
guard probes are autonomous agents.

## Observed production behavior

The public ACTIVE runtime visibly executed the escalated three-verdict guard:

1. **IDENTITY_REVERT**
   - future change: customer_identity account_id → email
   - result: **MERGE_BLOCKED**
   - visible finding: AGENT_DRIFT against RESOLVED_CANON
   - same-diff counterfactual without decision memory: **DECISION_REQUIRED**
   - visible tests during changed state: 33 passed / 4 failed
   - exact workspace restoration shown

2. **COMPATIBLE_CHANGE**
   - future change: notification wording only
   - result: **MERGE_ALLOWED**
   - no semantic concept changed
   - same-diff counterfactual without decision memory: **DECISION_REQUIRED**
   - visible tests during changed state: 37 passed / 0 failed
   - exact workspace restoration shown

3. **MONEY_UNIT_DRIFT**
   - future change: Ledger money unit integer_cents → decimal_dollars
   - result: **DECISION_REQUIRED**
   - all tests remain green
   - source authority is absent for the unit choice
   - exact workspace restoration shown

After all three probes, the UI showed:

- 3 of 3 future changes judged
- workspace restored / exact bytes
- SEMANTICALLY READY AGAIN
- regression contract 7 / 7

The proof drawer was also opened and showed real code diffs and hash/restoration
evidence for the guard probes.

## What this proves

- The escalated three-verdict guard is deployed on the public Cloudflare runtime.
- Decision memory changes the semantic verdict for the same future change.
- The guard is not a blanket blocker: a compatible change can be MERGE_ALLOWED.
- A test-green change can still produce DECISION_REQUIRED when it exposes a
  source-silent semantic decision.
- Guard probes restore the verified workspace after evaluation.

## What this does NOT prove

Still pending:

- separate-browser-session isolation on the public runtime
- public mobile smoke
- live read of x-collider-worker-version matched to the Workers Builds commit
- live page-header/CSP confirmation
- external Real-User / Outsider Break Test

Truth boundary remains:

- interpretations: PRESEEDED
- human decision: INTERACTIVE_WEB
- guard probes: fixed controlled changes, not agents
- fresh-agent replay: NOT_EXECUTED / PENDING_LIVE_BOB
