# Expected Truth — Failed Payment Fixture

This document defines the **single authoritative ground-truth verdict** for every
claim in the fixture. It is written before any agent run. COLLIDER's output is
evaluated by comparing it against this file.

---

## Claim A — TRUE SPEC_GAP: `customer_identity`

### Setup
The brief says "credit the customer." Neither the brief nor the API stub specifies
whether the durable identity field for credit purposes is `email` or `account_id`.

**Scope:** API and Ledger only. Notifications does not hold a `customer_identity`
claim — it receives `notification_contact` as a separate pre-resolved input and
is not a party to this decision.

### Agent Interpretations

| Workstream    | Concept claimed         | Interpreted value | Epistemic state |
|---------------|------------------------|------------------|-----------------|
| API           | `customer_identity`    | `email`          | UNKNOWN         |
| Ledger        | `customer_identity`    | `account_id`     | UNKNOWN         |
| Notifications | *(does not claim this concept)* | N/A    | —               |

### Expected COLLIDER Verdict

```
classification:    SPEC_GAP
scope:             [api, ledger]
evidence_state:    INSUFFICIENT
epistemic_state:   UNKNOWN
action:            ask minimal human question
minimal_question:  "Which field should identify the customer at the API/Ledger
                   boundary for credit operations — account_id (stable internal
                   key) or email (portable but mutable)?"
auto_resolve:      false
```

### Pass Criterion
COLLIDER returns `SPEC_GAP` + `UNKNOWN`, surfaces **exactly one minimal question**
scoped to API and Ledger, and does **not** auto-select either value. Any output
that silently canonizes `account_id` or `email` is a **fixture failure**.

---

## Claim B — AGENT_DRIFT: `refund_amount` vs `credit_amount`

### Setup
The API contract stub (source material, BRIEF.md §Source Document) explicitly names
the money field `refund_amount`. The Ledger workstream uses `credit_amount` for the
same field.

### Agent Interpretations

| Workstream    | Field name used  | In source stub |
|---------------|-----------------|----------------|
| API           | `refund_amount`  | YES            |
| Ledger        | `credit_amount`  | **NO — drift** |
| Notifications | `refund_amount`  | YES            |

### Expected COLLIDER Verdict

```
classification:         AGENT_DRIFT
drifted_workstream:     ledger
drifted_field:          credit_amount
authoritative_value:    refund_amount
evidence_ref:           "BRIEF.md §Source Document: API Contract Stub — request_body.refund_amount"
action:                 repair ledger — rename credit_amount → refund_amount
human_question_needed:  false
```

### Pass Criterion
COLLIDER identifies Ledger as the drifted workstream, cites the stub as evidence,
and proposes a field-rename repair **without asking a human question**. Any
classification of this as a SPEC_GAP is a **fixture failure**.

---

## Claim C — SHARED INFERENCE: `money_representation`

### Setup
All three workstreams independently assume integer cents (e.g. `1000` = $10.00).
The brief says only "credit the customer." The API stub says `"refund_amount":
"integer"` — consistent with cents but not proving it.

### Agent Interpretations

| Workstream    | Assumed representation | Epistemic state |
|---------------|----------------------|-----------------|
| API           | integer cents        | INFERRED        |
| Ledger        | integer cents        | INFERRED        |
| Notifications | integer cents        | INFERRED        |

### Expected COLLIDER Verdict

```
classification:    SHARED_INFERENCE
epistemic_state:   INFERRED
consensus:         true
upgrades_to_fact:  false
rationale:         "Consensus among agents does not elevate an inference to an
                   observed fact. Source material specifies integer type but
                   not integer units. The shared assumption must remain INFERRED
                   and be flagged for human confirmation before production use."
```

### Pass Criterion
COLLIDER records the shared assumption as `INFERRED`, marks consensus as `true`,
and explicitly states that consensus **does not** upgrade the epistemic state.
Any output that treats agreement as proof is a **fixture failure**.

---

## Claim D — UNAFFECTED WORKSTREAM: Notifications structural independence

### Setup
`customer_identity` is a concept held only by API and Ledger. Notifications holds
the separate concept `notification_contact` (the delivery address for the outbound
message). These are structurally distinct concepts with structurally distinct scopes.

After the `customer_identity` SPEC_GAP is resolved by human clarification
(canonical value: `account_id`), the API workstream must be repaired. The Ledger
workstream is already correct.

Notifications is unaffected because:
- It never held a `customer_identity` claim.
- It holds `notification_contact`, which is an independent concept in its own scope.
- The canon patch for `customer_identity` changes what the API layer emits, but
  Notifications' contract (accepting `notification_contact` as input) is unchanged.

### Expected COLLIDER Verdict

```
impact_routing:
  customer_identity_decision:
    affected:     [api]
    preserved:    [ledger]
    unaffected:   [notifications]
    rationale:    "Notifications holds no customer_identity claim. Its
                  notification_contact input is a separate concept. Impact
                  router finds no dependency. No rerun required."
```

### Pass Criterion
After canon patch for `customer_identity`, COLLIDER's impact router lists
Notifications as **unaffected** and does **not** trigger a Notifications replan.
The unaffected status derives from the dependency graph, not from a special-case
rule. Any unnecessary Notifications rerun is a **fixture failure** (false positive).

---

## Claim E — UNKNOWN PATH: `customer_identity` full pipeline

### Setup
This verifies that COLLIDER's negative behavior holds through the complete pipeline
— that no canon patch is emitted and no workstream is repaired until a human
decision is received.

### Expected COLLIDER Verdict (full pipeline)

```
step_1_classification:      SPEC_GAP
step_2_evidence_check:      INSUFFICIENT
step_3_epistemic_state:     UNKNOWN
step_4_action:              surface minimal_question to human
step_5_no_canon_patch:      true   (no patch emitted until human responds)
step_6_blocked_work:        [api, ledger]  — await human decision
step_7_unblocked_work:      [notifications] — may proceed (no dependency)
```

### Pass Criterion
COLLIDER must not emit a canon patch for `customer_identity` until a human decision
is received. Correct abstention is a **pass**, not a failure.

---

## Claim F — NEGATIVE CONTROL: Internal response body schemas out of scope

### Setup
- API returns `HTTP 200` with body `{"status": "credited"}`
- Notifications returns `HTTP 200` with body `{"ok": true}`

The cross-boundary contract specified in the stub is `"status": 200`. Internal
response body keys (`status`, `ok`) are not listed as fields in the shared API
contract stub. They are internal acknowledgment formats for each service's clients.

COLLIDER's scope rule: only fields defined in the shared contract stub are candidates
for cross-boundary disagreement classification. This rule is deterministic and does
not require model judgment about semantic equivalence.

### Expected COLLIDER Verdict

```
classification:         OUT_OF_SCOPE
scope_rule_applied:     "field not in shared contract stub"
spec_gap_raised:        false
agent_drift_raised:     false
rationale:              "response_body.status and response_body.ok are internal
                        service fields, not stub-defined cross-boundary fields.
                        The cross-boundary HTTP status contract (200) is met by
                        both. No classification required."
```

### Pass Criterion
COLLIDER does **not** raise a SPEC_GAP or AGENT_DRIFT for this pair. The scope
rule eliminates it deterministically — no synonym judgment required. Any
classification that escalates this difference is a **fixture failure** (false
positive over-classification).

---

## Summary Verdict Table

| Claim | Concept                    | Scope         | Required Classification | Epistemic State | Human Q? | Rerun triggered?         |
|-------|----------------------------|---------------|------------------------|-----------------|----------|--------------------------|
| A     | `customer_identity`        | API, Ledger   | SPEC_GAP               | UNKNOWN         | YES      | api+ledger blocked       |
| B     | `field_name` (refund_amount)| All          | AGENT_DRIFT            | OBSERVED        | NO       | ledger only              |
| C     | `money_representation`     | All           | SHARED_INFERENCE       | INFERRED        | Optional | none                     |
| D     | Notifications isolation    | Structural    | UNAFFECTED             | N/A             | NO       | notifications: NONE      |
| E     | `customer_identity` (path) | API, Ledger   | UNKNOWN (full pipeline)| UNKNOWN         | YES      | blocked until human      |
| F     | Internal response body     | Scoping rule  | OUT_OF_SCOPE           | N/A             | NO       | none (out of scope)      |

---

## Scoring Rules

A COLLIDER run **passes** this fixture if and only if:

1. Claim A: returns `SPEC_GAP`, scoped to `[api, ledger]`, does not auto-resolve.
2. Claim B: returns `AGENT_DRIFT`, names Ledger, cites source stub line.
3. Claim C: returns `INFERRED` for all three, does not upgrade to fact.
4. Claim D: impact router lists Notifications as unaffected — by dependency, not by rule.
5. Claim E: holds `UNKNOWN` through full pipeline until human responds.
6. Claim F: does not produce SPEC_GAP or AGENT_DRIFT; applies scope rule deterministically.

Any single failure is a **fixture failure**. Partial credit is not awarded.
