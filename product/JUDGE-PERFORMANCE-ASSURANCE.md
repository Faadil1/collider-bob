# Judge Performance Assurance — 2026-09-27

## Verdict

**PROVEN FOR DEMO LOCK**

The current public build has enough product depth, runtime proof, narrative compression,
and evidence integrity to enter final media packaging.

The hackathon submission package was delivered at the deadline. The exact submitted
repository snapshot is preserved at `archive/submission-deadline-2026-09-27`.
Any later walkthrough or README polish is post-submission presentation material,
not new product functionality.

---

## Judge memory

> **When AI agents disagree, COLLIDER finds the decision the specification forgot to make.**

Second-act line:

> **Tests say pass or fail. COLLIDER adds a third answer: nobody decided this yet.**

The category is **Semantic CI for Agentic Software Development**.

---

## Rubric assurance

### 1. Application of Technology — PASS WITH TRUTH BOUNDARY

What is proven:

- IBM Bob 2.0 was used directly in the repository as a development agent.
- Preserved Bob work shows repository reading, file creation/modification, runtime/test
  work, and iterative continuation across two tasks.
- COLLIDER was designed around parallel-agent disagreement as an ambiguity signal.
- The finished public product is an active system, not a static mockup:
  decision compilation, targeted repair, regression contract, memory, three-way guard,
  exact restoration, and Cloudflare Container execution all run for real.

Boundary that must stay visible:

- the canonical interpretation objects are **PRESEEDED**, not live Bob-generated;
- the three guard probes are controlled future changes, not autonomous agents;
- replay in the public demo session remains unexecuted;
- separate Bob evidence records Attempt 01 as REPLAY_FAIL and Attempt 02 as a
  targeted-repair REPLAY_PASS with a 7/7 withheld contract.

Judge risk:
A judge may confuse "built with Bob" with "canonical proof generated live by Bob."

Mitigation:
Show Bob Task Session Summary/screenshots separately and narrate the distinction in one sentence.

### 2. Presentation — PASS

The demo has one clean causal arc:

`GREEN LOCALLY → COLLISION → SOURCE-AWARE CLASSIFICATION → ONE HUMAN DECISION → 2→0 → MEMORY → THREE FUTURE VERDICTS`

The three verdicts are easy to remember:

- **MERGE_BLOCKED** — violates resolved canon;
- **MERGE_ALLOWED** — harmless semantic change;
- **DECISION_REQUIRED** — tests pass, but the source never decided.

The signature moment is strong:

> **37/37 tests pass. COLLIDER still returns DECISION_REQUIRED.**

Public desktop and real-iPhone runs reproduce the flow.

### 3. Business Value — PASS WITHOUT INVENTED ROI

The demonstrated value mechanism is concrete:

- catch cross-workstream semantic mismatch before it silently becomes shared reality;
- distinguish agent error from missing product/specification decisions;
- ask one bounded clarification instead of broad rework;
- repair only affected code;
- persist the decision so future work is judged against it;
- avoid both false confidence and blanket blocking.

Do **not** claim:
- percentage productivity gains;
- time savings not measured;
- production-scale generalization.

### 4. Originality — PASS

COLLIDER is not presented as generic:
- merge conflict detection;
- shared memory;
- automated clarification;
- multi-agent review.

The distinctive mechanism is:

`interpretation variation → implementation divergence → source-aware truth test → missing decision → executable decision memory → future semantic CI verdict`

The third verdict — **DECISION_REQUIRED even while all tests pass** — is the strongest judge-facing differentiator.

---

## Demo timing assurance

The final video must remain **≤ 3:00** and contain **≥ 90 seconds of actual product**.

Target cut:

- 0:00–0:12 — problem / hook
- 0:12–2:28 — actual product
- 2:28–2:42 — Bob usage proof + provenance boundary
- 2:42–2:55 — business/originality close

Target total: **~2:55**.

Do not let architecture explanation consume demo time.

---

## Judge confusion checks

### "Why not just tests?"
Because MONEY_UNIT_DRIFT keeps **37/37 tests green** while exposing a source-silent cross-workstream decision.

### "Why not just block every change?"
Because COMPATIBLE_CHANGE returns **MERGE_ALLOWED**.

### "Why is memory useful?"
The same identity diff is:
- **MERGE_BLOCKED** with decision memory;
- **DECISION_REQUIRED** without it.

Memory changes the verdict.

### "What happens if the system does not know?"
**KEEP UNKNOWN** writes no canon and applies no repair.

### "Is this live Bob?"
Bob was genuinely used to build/refine the system. The canonical interpretations are PRESEEDED, and fresh-agent replay is not claimed.

---

## Evidence anchors

- public three-verdict guard:
  `evidence/runtime/PUBLIC-THREE-VERDICT-GUARD-2026-09-27.md`
- real-device mobile:
  `evidence/runtime/PUBLIC-MOBILE-PROVENANCE-2026-09-27.md`
- session isolation:
  `evidence/runtime/PUBLIC-SESSION-ISOLATION-2026-09-27.md`
- runtime/commit binding:
  `evidence/runtime/RUNTIME-COMMIT-BINDING-2026-09-27.md`
- live CSP/security headers:
  `evidence/runtime/LIVE-CSP-HEADERS-2026-09-27.md`
- canonical comparison:
  `evidence/comparisons/baseline-001-vs-local-resolved-004.md`

---

## Demo Lock decision

**EARNED, subject to unchanged truth boundaries.**

No further product feature is required for the submission demo.

From this point forward, changes should be limited to:
- judge comprehension;
- packaging;
- evidence clarity;
- bug fixes;
- submission integrity.

Any material product change reopens relevant gates.
