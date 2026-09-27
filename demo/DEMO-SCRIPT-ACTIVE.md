# COLLIDER — Final Active Demo Script (≤ 3 min, ≥ 90 s actual product)

**Target total:** ~2:55  
**Actual product:** ~2:15+

**Judge memory sentence:** When AI agents disagree, COLLIDER finds the decision
the specification forgot to make.

**Second-act line:** Tests say pass or fail. COLLIDER adds a third answer:
*nobody decided this yet.*

Everything shown in ACTIVE MODE is the real public product.

Interpretations are PRESEEDED. Never call them live Bob-generated.

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
| 2:10–2:28 | PROOF drawer | RECEIPT / PROVENANCE | "Every step has receipts, diffs, hashes and exact restoration. Public Cloudflare container. PRESEEDED interpretations. Interactive human decision. Fresh-agent replay is not claimed." |
| 2:28–2:42 | Bob evidence screenshot / Task Summary | — | "IBM Bob was a load-bearing development agent in the repository: it read project state, changed runtime and test files, and helped harden the evidence. The canonical interpretations shown here are still PRESEEDED." |
| 2:42–2:55 | close | product + title | "Traditional CI asks whether code passes. COLLIDER asks whether the team ever decided what the code is supposed to mean. Fuzz the specification. Repair the decision. Prove the system understands it." |

## Recording rules

- Keep the final video under **3:00**.
- Maintain at least **90 seconds of actual product**.
- Do not cut between a product click and its result.
- Do not claim:
  - percentage productivity improvement;
  - unmeasured time savings;
  - production-scale generalization;
  - PRESEEDED interpretations as LIVE_BOB;
  - controlled guard probes as autonomous agents;
  - Mars Climate Orbiter as an incident COLLIDER would have prevented.
- If the public runtime becomes unavailable, a local recording must be labeled
  LOCAL ACTIVE DEMO. Prefer the already-proven public runtime.
