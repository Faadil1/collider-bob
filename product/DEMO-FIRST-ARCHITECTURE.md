# COLLIDER — Demo-First Architecture

## Product brief (fixture)

> "After a failed charge, credit the customer and notify them."

Workstreams: **API**, **Ledger**, **Notifications**

---

## Part 1 — Disagreement Classifier

### 5-Step Classification Algorithm

The classifier operates on a pair of structured interpretation objects. Each object is the output
of a workstream agent for a single shared concept (e.g. `customer_identity`, `field_name`,
`money_representation`).

---

**Step 0 — Scope filter (pre-normalization)**

Before normalization, filter the concept set to only those concepts whose values are defined
as fields in the shared API contract stub (BRIEF.md §Source Document).

- The stub defines: `charge_id`, `refund_amount`, `notification_contact`, HTTP status `200`.
- Internal response body keys (e.g. `status`, `ok`) are **not** stub fields.
- Any concept that maps only to internal body keys is classified `OUT_OF_SCOPE` and excluded
  from further classification.

This rule is **fully deterministic**: it is a lookup against the committed stub field list,
not a judgment about semantic equivalence. The negative control case (different response body
syntax) is eliminated here without invoking any synonym table or model call.

---

**Step 1 — Normalize values**

Produce a canonical form for each candidate value before any comparison.

- Lowercase all strings.
- Strip leading/trailing whitespace; collapse internal whitespace to a single space.
- No synonym table required. The scope filter (Step 0) removes the only case that previously
  required one. Normalization is now pure string canonicalization.

---

**Step 2 — Check for agreement**

If all normalized workstream values are equal → return `NO_DISAGREEMENT`. Stop.

This step is fully deterministic.

---

**Step 3 — Check source evidence for explicit specification**

Retrieve source evidence (product brief, spec documents, architecture decision records) and check
whether the source explicitly names one of the candidate values as the required choice.

Explicit specification means: the source document uses the exact term or a committed synonym, in
a context that unambiguously assigns it as the required value for this concept.

Decision rules:
- If the source is explicit and **all** workstreams match it → `NO_DISAGREEMENT` (already caught
  by Step 2, but confirmed by evidence).
- If the source is explicit and **one or more** workstreams contradict it → `AGENT_DRIFT` for
  each contradicting workstream. The compliant workstream(s) are not implicated.
- If the source **names** the concept but does not specify a value → proceed to Step 4.
- If the source is **silent** (concept not mentioned) → proceed to Step 4.

**Determinism boundary:** Whether the source text "explicitly specifies" a value requires
a model to locate, read, and interpret a passage. This is a model judgment, not a string match.
The retrieval step (finding the passage) can be automated; the interpretation step (does this
passage decide the question?) requires judgment and must be logged so it can be audited.
Mark the evidence reference as `OBSERVED` only when the passage is unambiguous. Mark it
`INFERRED` when interpretation was required.

---

**Step 4 — Classify undecided disagreement**

Source is silent or does not decide the question. Multiple candidate values remain plausible.

- If two or more distinct plausible values exist with no source basis for preferring one
  → `SPEC_GAP`.
- If evidence is present but insufficient to confirm or eliminate any candidate
  → upgrade to `UNKNOWN` (absorbs `SPEC_GAP` when evidence quality is degraded).
- `SPEC_GAP` means: the source should have decided this but did not. A human decision is
  required. Do not auto-resolve.

**Determinism boundary:** Deciding whether a candidate value is "plausible" requires model
judgment. A model may incorrectly evaluate plausibility. This must be treated as INFERRED, not
OBSERVED. When uncertain, escalate to `UNKNOWN`.

---

**Step 5 — Default to UNKNOWN**

If evidence is unavailable, stale, conflicting, or the classifier cannot complete Steps 3–4 with
sufficient confidence:

→ return `UNKNOWN`.

Do not invent a canon. Do not narrate a `SPEC_GAP` as resolved. `UNKNOWN` is a valid and
required output.

This step is fully deterministic as a fallback rule. The difficulty is in recognizing when
evidence quality is insufficient — which again requires model judgment applied conservatively.

---

### Determinism audit

| Step | Deterministic? | Notes |
|------|---------------|-------|
| 0. Scope filter | **Yes** | Lookup against committed stub field list; no model call |
| 1. Normalize | **Yes** | Pure string canonicalization; no synonym table |
| 2. Agreement check | **Yes** | String equality on normalized values |
| 3. Source evidence retrieval | Partial — retrieval automatable; interpretation requires model judgment | Log evidence reference + epistemic state |
| 3. AGENT_DRIFT decision | Partial — depends on Step 3 interpretation quality | Requires logged source passage; must be auditable |
| 4. SPEC_GAP vs UNKNOWN | No — requires model assessment of plausibility and evidence sufficiency | Must be conservative; prefer UNKNOWN on uncertainty |
| 5. UNKNOWN fallback | **Yes** | Applied when Steps 3–4 cannot reach a confident result |

**Honest summary:** Steps 0, 1, 2, and 5 are fully deterministic. Steps 3 and 4 involve model
judgment. The system's integrity depends on logging those judgment steps, marking their evidence
state correctly (OBSERVED / INFERRED / UNKNOWN), and never narrating a model judgment as a
deterministic fact.

---

### Fixture classification results

| Concept | Scope | Values | Classification | Reasoning |
|---------|-------|--------|---------------|-----------|
| `customer_identity` | API, Ledger | account_id / email | `SPEC_GAP → UNKNOWN` | Source silent on identity field; two plausible values; no basis for preferring one |
| `field_name` | All | refund_amount vs credit_amount | `AGENT_DRIFT` (Ledger) | Brief explicitly uses "refund_amount"; Ledger contradicts it |
| `money_representation` | All | integer_cents (all three) | `NO_DISAGREEMENT` — `SHARED_INFERRED` | All agree; source silent; agreement is noted but not upgraded to OBSERVED |
| Internal response bodies | N/A | `{"status":"credited"}` / `{"ok":true}` | `OUT_OF_SCOPE` (Step 0) | Not stub-defined cross-boundary fields; scope filter eliminates before classification |

---

## Part 2 — Canon + Impact Routing

### Scenario: human resolves `customer_identity` SPEC_GAP

Human decision: **`account_id` is the canonical customer identity field.**

---

### Canon patch

```json
{
  "concept": "customer_identity",
  "canonical_value": "account_id",
  "decision_source": "human",
  "decided_by": "tech-lead",
  "timestamp": "2025-01-01T00:00:00Z",
  "git_commit": "abc1234",
  "evidence_state": "OBSERVED",
  "rationale": "Ledger is the system of record for financial transactions; account_id is the stable financial identity. Email is mutable and is not a financial identifier. notification_contact is a delivery concern and a separate concept — not a party to this decision.",
  "prior_state": "SPEC_GAP",
  "applies_to_run": "run-001"
}
```

---

### Impact set

| Workstream | Concept held | Prior value | Canon value | Status after patch |
|------------|-------------|-------------|-------------|-------------------|
| API | `customer_identity` | `email` | `account_id` | **REPAIR** — contradicts canon |
| Ledger | `customer_identity` | `account_id` | `account_id` | **PRESERVE** — already canonical |
| Notifications | `notification_contact` | `email_address` | N/A | **NO DEPENDENCY** — holds a different concept; not in scope of this patch |

**Rationale for Notifications being out of scope:** Notifications never held a `customer_identity`
claim. Its concept is `notification_contact` — a separate delivery address concern. The impact
router determines this by checking the `consumed_by` field of the canon patch concept across all
workstream interpretation objects. Notifications does not appear. No special-case rule required.

---

### Targeted repair trigger

```
REPAIR REQUIRED:   workstream=API   reason="customer_identity = email; canon = account_id"
NO REPAIR:         workstream=Ledger   reason="customer_identity = account_id; matches canon"
NO DEPENDENCY:     workstream=Notifications   reason="concept=notification_contact; not in customer_identity scope"
```

Only the API workstream reruns. Ledger and Notifications are preserved as-is.

---

### Evidence binding on the repair

```json
{
  "repair_trigger": {
    "concept": "customer_identity",
    "canon_patch_commit": "abc1234",
    "canon_patch_timestamp": "2025-01-01T00:00:00Z"
  },
  "workstream": "API",
  "repair_type": "targeted",
  "prior_value": "email",
  "canonical_value": "account_id",
  "repair_commit": "def5678",
  "repair_timestamp": "2025-01-01T00:01:00Z",
  "evidence_state": "OBSERVED"
}
```

---

## Part 3 — Classifier in the Full Loop

```
Bob Plan
  └─ Brief: "After a failed charge, credit the customer and notify them."
       │
       ├─ Workstream: API
       │    └─ interpretation → { customer_identity: "email", field_name: "refund_amount",
       │                           money_representation: "integer_cents" }
       ├─ Workstream: Ledger
       │    └─ interpretation → { customer_identity: "account_id", field_name: "credit_amount",
       │                           money_representation: "integer_cents" }
       └─ Workstream: Notifications
            └─ interpretation → { notification_contact: "email_address",
                                   money_representation: "integer_cents" }
              ↑ holds different concepts; no customer_identity claim

Step 0 — Scope filter:
  internal body keys (status, ok) → OUT_OF_SCOPE (not stub fields)

Reconciler groups stub-scoped shared concepts:
  customer_identity → [api:email, ledger:account_id]   (Notifications not a party)
  field_name        → [api:refund_amount, ledger:credit_amount]
  money_repr        → [api:integer_cents, ledger:integer_cents, notif:integer_cents]

Classifier runs per concept:
  customer_identity → SPEC_GAP / UNKNOWN           (source silent; two values; API+Ledger only)
  field_name        → AGENT_DRIFT (Ledger)          (brief says refund_amount; Ledger says credit_amount)
  money_repr        → NO_DISAGREEMENT (SHARED_INFERRED) (all agree; source silent; not upgraded)

AGENT_DRIFT (field_name):   evidence-grounded repair of Ledger only; no human question
SPEC_GAP (customer_identity): minimal clarification → human decides account_id
Canon patch → impact router:
  API in consumed_by → REPAIR
  Ledger in consumed_by, already canonical → PRESERVE
  Notifications: not in consumed_by for customer_identity → NO DEPENDENCY
```

---

## Part 6 — Demo Signature Sequence

**Emotional arc:**
> "Everything looked green locally — but the agents were building incompatible assumptions."
> "The specification never decided."
> "One question repairs only what actually depended on it."

---

### Step 1 — Brief presented

Display the fixture brief verbatim:
> *"After a failed charge, credit the customer and notify them."*

Framing: this is the complete specification. Three workstreams will receive this text.

---

### Step 2 — Bob Plan decomposes the brief

Bob Plan mode produces an explicit task decomposition:
- Workstream API: implement the credit endpoint and return a response.
- Workstream Ledger: record the credit in the ledger system.
- Workstream Notifications: send the customer notification.

Each workstream has explicit interpretation boundaries. No shared state. No coordination.

---

### Step 3 — Subagents execute independently

Three Bob Agent subagents run in parallel. Each reads only the brief and its workstream scope.
No inter-agent communication. Each produces code and a structured interpretation object.

---

### Step 4 — Local checks pass

Each workstream's local tests run against its own implementation in isolation. All pass.
Git conflict count: 0. No linting errors. No build failures.

**Pause here.** Green across the board — locally.

> *"Everything looked green locally."*

---

### Step 5 — Interpretations extracted

COLLIDER reads the structured interpretation objects from each workstream. No code is read yet —
only the declared interpretations.

```
API:           customer_identity = email
               field_name        = refund_amount
               money_repr        = integer_cents

Ledger:        customer_identity = account_id
               field_name        = credit_amount   ← will become AGENT_DRIFT
               money_repr        = integer_cents

Notifications: notification_contact = email_address  ← different concept; no customer_identity claim
               money_repr           = integer_cents
```

---

### Step 6 — Reconciler groups shared concepts

COLLIDER groups interpretations by concept across workstreams. Three workstreams, four shared
concepts. The reconciler does not classify yet — it only groups.

---

### Step 7 — Classifier runs

Step 0 (scope filter) + Steps 1–5 execute per concept.

- `internal body keys (status / ok)`: Step 0 scope filter → `OUT_OF_SCOPE`. Eliminated
  deterministically. No model call. COLLIDER does not raise a false alarm.
- `money_representation`: all agree → `NO_DISAGREEMENT` / `SHARED_INFERRED`. Noted; not escalated.
- `field_name`: source check → brief says "refund_amount" → Ledger says "credit_amount" →
  `AGENT_DRIFT` (Ledger).
- `customer_identity`: scope API+Ledger only → source silent → two distinct values, both plausible →
  `SPEC_GAP → UNKNOWN`.

---

### Step 8 — AGENT_DRIFT repair (field_name)

Evidence: brief text, exact word "refund_amount", line reference.
Repair instruction generated for Ledger only.
Ledger agent reruns with the evidence-grounded correction.
Ledger test re-run: passes.

> *"This one the spec decided. The agent got it wrong."*

---

### Step 9 — SPEC_GAP surface

`customer_identity` displayed for the two parties that hold it:

```
Scope: API, Ledger

API    → email
Ledger → account_id

Source evidence: NONE. The brief never names an identity field.
Classification: SPEC_GAP / UNKNOWN

(Notifications is not in scope — it holds notification_contact, a separate concept.)
```

> *"The specification never decided."*

---

### Step 10 — Minimal clarification issued

One question, not three:

> "Which field should identify the customer in the refund workflow — email, account_id,
> or some other value?"

This is the minimum question that resolves the ambiguity. It is not a product decision made by
COLLIDER. It is a question addressed to the human decision-maker.

---

### Step 11 — Human decides

> Decision: `account_id`

One answer. Entered once.

---

### Step 12 — Canon patch written

The decision is persisted as a canon patch with commit hash, timestamp, and decision source.
This is now a durable, auditable artifact — not a chat message.

---

### Step 13 — Impact router runs

| Workstream | Uses `customer_identity`? | Value matches canon? | Action |
|------------|--------------------------|---------------------|--------|
| API | Yes — uses `email` | No | **REPAIR** |
| Ledger | Yes — uses `account_id` | Yes | Preserve |
| Notifications | No — receives resolved target | N/A | Preserve |

> *"One question. One repair."*

---

### Step 14 — Targeted repair

API workstream reruns with the canon patch in scope. Ledger and Notifications are untouched.
Post-repair tests run: all pass.

The evidence record shows:
- what changed
- what was preserved
- which decision drove the repair
- the commit binding the decision to the code

---

### Step 15 — Evidence record presented

Display the full run record:

- `manifest.json` — run metadata
- `interpretations/` — what each agent said
- `classifications.json` — what COLLIDER decided and why
- `canon-patches/customer_identity.json` — the human decision, durably stored
- `impact-set.json` — what was repaired, what was preserved
- `tests-before.txt` — green (they were always green)
- `tests-after.txt` — still green
- `failures.json` — preserved failures from the run (none erased)
- `metrics.json` — observed metrics only (no preset improvement claims)

> *"Everything was still green. But now the agents were building the same reality."*

---

## Appendix — Fixture disagreement map

| # | Concept | Scope | Values | Classification | Workstream implicated |
|---|---------|-------|--------|---------------|-----------------------|
| 1 | `customer_identity` | API, Ledger | account_id / email | `SPEC_GAP / UNKNOWN` | API, Ledger (Notifications holds separate concept) |
| 2 | `field_name` | API, Ledger | refund_amount vs credit_amount | `AGENT_DRIFT` | Ledger |
| 3 | `money_representation` | All | integer_cents (all) | `SHARED_INFERRED` | None escalated |
| 4 | Internal response bodies | N/A | `{"status":"credited"}` / `{"ok":true}` | `OUT_OF_SCOPE` (Step 0) | None |

---

## Implementation Sequence

The sequence below is ordered by dependency. Do not begin a step until its prerequisite is committed.

| Step | Component | Prerequisite | Output |
|------|-----------|--------------|--------|
| 1 | Interpretation schema validation | schemas/interpretation.schema.json (exists) | Verify 6 fixture interpretation objects pass schema |
| 2 | Reconciler script | Interpretation objects | concept-grouped disagreement map |
| 3 | Evidence resolver | BRIEF.md committed | Per-concept evidence state (OBSERVED / INFERRED / UNKNOWN) |
| 4 | Rule-based classifier | Reconciler + evidence resolver | classifications.json per fixture |
| 5 | Canon patch writer | Human clarification input | canon-patches/<concept>.json |
| 6 | Impact router | Canon patch + interpretation downstream_consumers | impact-set.json |
| 7 | Baseline agent run | Fixture brief, no COLLIDER path | evidence/runs/baseline-001/ |
| 8 | COLLIDER agent run | All components above, Bob parallel subagents | evidence/runs/collider-001/ |
| 9 | Fixture verification | EXPECTED-TRUTH.md, both run outputs | Pass/fail per claim A–F |
| 10 | Evidence binding | Git commit SHA at step 8 completion | manifest.json finalized |

**Critical path for demo:** Steps 1–6 can be built and tested against committed fixture files without any live Bob session. Steps 7–10 require a live session. Build and verify Steps 1–6 first.

---

## Technical Blockers

### BLOCKER-01 — Agent divergence is not guaranteed (UNKNOWN)

Parallel Bob subagents with access to the same brief may converge on the same interpretations, producing no disagreements to classify. This is the single most critical unknown.

**Mitigation:** Design workstream prompts with explicit interpretation boundaries. If live divergence proves unreliable, fall back to committed interpretation objects with disclosure. The classifier behavior — not the live generation — is what the demo proves.

**Status:** UNKNOWN until a live session is run.

---

### BLOCKER-02 — Concept vocabulary alignment (UNKNOWN)

The reconciler groups interpretations by `concept` name. If Bob agents name concepts differently (`customer_id` vs `user_identity`), the reconciler misses the disagreement.

**Mitigation:** Workstream prompts must constrain the concept vocabulary. The interpretation schema's `concept` field should be drawn from a controlled enumeration for the fixture. Add a vocabulary table to the workstream prompt: `customer_identity`, `field_name`, `money_representation`, `success_response`.

**Status:** UNKNOWN until a live session is run.

---

### BLOCKER-03 — Evidence resolver scope (INFERRED risk)

The evidence resolver must find "refund_amount" in BRIEF.md to classify the `field_name` disagreement as AGENT_DRIFT. If the resolver's text search misses it, AGENT_DRIFT degrades to UNKNOWN. This is the most dangerous silent failure (FM-02).

**Mitigation:** For the fixture, use exact string search on the committed BRIEF.md. The phrase "refund_amount" appears verbatim. This is a string-match, not semantic retrieval. The risk is low for the fixture but must be verified by running the resolver before the demo.

**Status:** INFERRED low risk for the fixture; verify before demo.

---

### BLOCKER-04 — Canon patch binding on repair agent (INFERRED risk)

The repair agent for the API workstream must incorporate the canon patch. If the patch is not passed explicitly as context — or if the agent ignores it — the repair produces the same wrong output.

**Mitigation:** Pass the canon patch file path explicitly in the repair agent's system prompt. After repair, re-extract the interpretation object and verify the `customer_identity` value equals `account_id` before marking the run complete.

**Status:** INFERRED risk; mitigated by explicit patch injection and post-repair verification.

---

## Claims We Can Make (after a successful canonical run)

- COLLIDER detected a semantic disagreement that passed all unit tests (OBSERVED, if the run shows green tests + disagreement)
- COLLIDER classified the disagreement as SPEC_GAP because source evidence was absent (OBSERVED, if classifications.json shows evidence_state: INSUFFICIENT)
- One minimal question resolved the ambiguity (OBSERVED, if the run record shows exactly one human clarification)
- Only one workstream was repaired; two were preserved (OBSERVED, if impact-set.json confirms this)
- The negative path returned UNKNOWN and did not invent a canon (OBSERVED, if a run demonstrates this)

## Claims We Must Not Make (ever)

- COLLIDER would have prevented the Mars Climate Orbiter loss (forbidden; MCO was not an AI-agent failure)
- Any percentage improvement (forbidden until observed from real baseline vs COLLIDER comparison)
- Agent agreement is proof (forbidden; consensus is INFERRED at best)
- COLLIDER performs semantic merge or replaces Git or CI (non-goal; explicitly listed in PRD)
- Any Bob capability is load-bearing (all Bob claims are INFERRED until session evidence exists)
- A simulated or pre-authored run is a live execution (forbidden; must be disclosed in manifest.json)

