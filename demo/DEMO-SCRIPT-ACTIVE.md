# COLLIDER — Active Product Demo Script (≤ 3 min video, ≥ 90 s real product)

Supersedes the product beats of demo/DEMO-COMPRESSION-100S.md, which predates
ACTIVE MODE and the guard. That file remains the record of the compression
exercise.

**Judge memory sentence:** When AI agents disagree, COLLIDER finds the decision
the specification forgot to make.

**Second-act line:** Tests say pass or fail. COLLIDER adds a third answer:
*nobody decided this yet.*

Everything on screen is the real product in ACTIVE MODE (public Cloudflare
runtime, or `python3 demo-ui/server.py`). Interpretations are PRESEEDED; say
so. Never say "live Bob agents" about the interpretations.

| Time | Screen | Action | Say (≈) |
|---|---|---|---|
| 0:00–0:12 | title / brief | — | "Three agents built one feature from one sentence: *after a failed charge, credit the customer and notify them.*" |
| 0:12–0:30 | 01 DETECT | point at metrics | "30 tests pass. Three workstreams green. Two integration conflicts. Local success is not agreement." |
| 0:30–0:58 | 02 DECIDE | point at the three rows | "COLLIDER separates causes. The money field name is in the source — Ledger drifted, repaired from source, no question. Customer identity is not in the source — a SPEC_GAP, UNKNOWN. Money unit: everyone assumes cents, the source never says it — a shared assumption, INFERRED, not canon." |
| 0:58–1:05 | 02 DECIDE | hover KEEP UNKNOWN | "KEEP UNKNOWN is a real answer: nothing is canonized, nothing repaired." (optional: show it in a second session) |
| 1:05–1:22 | 03–06 COMPILE | click **USE account_id** | "One human answer compiles into a spec patch, two targeted repairs, a regression contract and decision memory. Two conflicts, zero. Semantically ready." |
| 1:22–1:45 | 07 GUARD A | click **TEST FUTURE AGENT CHANGES** | "A future agent reverts identity to email. Merge blocked — it contradicts the decision. Same diff without decision memory? Only a spec gap. Memory changed the verdict." |
| 1:45–2:00 | 07 GUARD B | **NEXT** | "A harmless wording change. Merge allowed. This is not a blanket block." |
| 2:00–2:25 | 07 GUARD C | **NEXT** | "Ledger switches to dollars. All 37 tests still pass. COLLIDER: decision required — the agents now disagree where the source is silent. It just found the next decision the spec forgot." |
| 2:25–2:45 | PROOF drawer | open CODE DIFF → RECEIPT → PROVENANCE | "Every step is a receipt: diffs, hashes, exact-byte restore. Cloudflare container, PRESEEDED interpretations, interactive web decision, Worker version. Fresh-agent replay: not executed — pending live Bob." |
| 2:45–2:58 | — | — | "Fuzz the specification. Repair the decision. Prove the system understands it." |

## Recording rules

- One continuous ACTIVE MODE session per take; reset with RESET SESSION or a
  new browser session (new container).
- Do not cut between a click and its result.
- Do not claim time savings, percentages, or that COLLIDER would have
  prevented any real incident.
- If the public runtime is unavailable, record the local server and label it
  LOCAL ACTIVE DEMO (the UI does this automatically).
