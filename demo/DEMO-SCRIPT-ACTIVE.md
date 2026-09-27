# COLLIDER — Final Active Demo Script (≤ 3 min, ≥ 90 s actual product)

**Target total:** ~2:55  
**Actual product:** ~2:15+

**Judge memory sentence:** When AI agents disagree, COLLIDER finds the decision
the specification forgot to make.

**Second-act line:** Tests say pass or fail. COLLIDER adds a third answer:
*nobody decided this yet.*

Everything shown in ACTIVE MODE is the real public product.

The public demo's built-in comparative interpretations are PRESEEDED. A separate
captured Bob proof run is genuinely LIVE_BOB and must be labeled as such.

| Time | Screen | Action | Say (≈) |
|---|---|---|---|
| 0:00–0:12 | title / failed-payment brief | — | "Three AI workstreams implement one sentence: after a failed charge, credit the customer and notify them." |
| 0:12–0:28 | 01 DETECT | point at metrics | "Thirty local tests pass. Three workstreams are green. Integration still finds two semantic conflicts." |
| 0:28–0:52 | 02 DECIDE | show classifications | "COLLIDER separates causes. refund_amount is explicit, so Ledger drifted. Customer identity is different: API chose email, Ledger account_id, and the source never decided. That is a SPEC_GAP — UNKNOWN." |
| 0:52–1:00 | 02 DECIDE | show shared assumption | "Everyone also assumes integer cents. The source never says that, so agreement stays INFERRED, not fact." |
| 1:00–1:16 | 03–06 COMPILE | click **USE account_id** | "One human answer compiles into a spec patch, two targeted repairs, a regression contract and decision memory. Two conflicts become zero. Semantically ready." |
| 1:16–1:37 | 07 GUARD A | run identity revert | "A future change puts email back. MERGE BLOCKED: it violates resolved canon. The same diff without decision memory becomes only DECISION REQUIRED. Memory changed the verdict." |
| 1:37–1:49 | 07 GUARD B | NEXT | "A harmless notification wording change: MERGE ALLOWED. This is not a blanket blocker." |
| 1:49–2:10 | 07 GUARD C | NEXT | "Ledger switches from cents to dollars. All 37 tests still pass. COLLIDER returns DECISION REQUIRED because the source never decided the money unit." |
| 2:10–2:24 | PROOF drawer | RECEIPT / PROVENANCE | "The public demo is explicit about provenance: its built-in comparison fixture is PRESEEDED. Separately, we ran the Bob-native protocol for real." |
| 2:24–2:38 | Bob evidence: LIVE_BOB | show selected capture J2/J3 | "Three isolated Bob agents disagreed on customer identity. COLLIDER validated the live provenance, kept the state UNKNOWN, and stopped for my human decision." |
| 2:38–2:49 | Bob evidence: replay | show selected capture J6 | "A fresh replay failed once, and we kept the failure. A second targeted replay, with only a general preserve-interface constraint, passed the hidden contract seven out of seven." |
| 2:49–2:55 | close | product + title | "Traditional CI asks whether code passes. COLLIDER asks whether the team ever decided what the code is supposed to mean. Fuzz the specification. Repair the decision." |

## Recording rules

- Keep the final video under **3:00**.
- Maintain at least **90 seconds of actual product**.
- Do not cut between a product click and its result.
- Do not claim:
  - percentage productivity improvement;
  - unmeasured time savings;
  - production-scale generalization;
  - PRESEEDED comparative fixture interpretations as LIVE_BOB;
  - Attempt 02 as an unconstrained first-try replay;
  - controlled guard probes as autonomous agents;
  - Mars Climate Orbiter as an incident COLLIDER would have prevented.
- If the public runtime becomes unavailable, a local recording must be labeled
  LOCAL ACTIVE DEMO. Prefer the already-proven public runtime.
