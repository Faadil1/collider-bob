# Baseline Contract — Failed Payment Fixture

## Purpose

This document defines how the **baseline run** and the **COLLIDER run** differ,
what metrics both must record, and how to compare them fairly. It also contains
the canonical interpretation object examples required by Part 2 of the fixture
design contract.

---

## Part 1 — Run Definitions

### Baseline Run

The baseline run executes the same brief and the same three workstreams **without
COLLIDER reconciliation**. Each workstream agent operates independently from brief
to implementation, emitting no structured interpretation objects, performing no
cross-boundary comparison, and receiving no canon patches.

**Baseline run sequence:**

```
1. Human engineer reads the brief.
2. Three workstream agents (API, Ledger, Notifications) each receive the brief
   independently.
3. Each workstream proceeds to implementation without comparing interpretations
   with the other workstreams.
4. All three outputs are submitted for integration.
5. Integration engineer discovers disagreements manually.
6. Rework cycles begin.
```

**What the baseline does NOT do:**
- Does not emit structured interpretation objects.
- Does not classify SPEC_GAP vs AGENT_DRIFT.
- Does not surface the `customer_identity` ambiguity before implementation.
- Does not detect the `credit_amount` drift in Ledger before integration.
- Does not identify that Notifications is unaffected by the identity decision.
- Does not protect the `money_representation` inference from being treated as fact.

---

### COLLIDER Run

The COLLIDER run executes the same brief and the same three workstreams **with
full COLLIDER reconciliation** before any workstream proceeds to final
implementation.

**COLLIDER run sequence:**

```
1. Human engineer reads the brief.
2. Bob Plan decomposes the task into workstream assignments.
3. Three workstream agents each emit a structured interpretation object for every
   cross-boundary concept they encounter.
4. Reconciler groups interpretations by concept and detects disagreements.
5. Evidence resolver compares each interpretation against BRIEF.md source material.
6. Classifier returns AGENT_DRIFT, SPEC_GAP, SHARED_INFERENCE, or EQUIVALENT
   for each disagreement group.
7. AGENT_DRIFT (credit_amount vs refund_amount) is repaired from evidence.
   Ledger is patched. No human question raised.
8. SPEC_GAP (customer_identity) raises one minimal human question. Blocked
   workstreams (API, Ledger) wait. Notifications proceeds unblocked.
9. Human answers the identity question. Canon patch is emitted.
10. Impact router identifies only API and Ledger as affected. Notifications is
    preserved — no rerun.
11. Only affected workstreams replan against the canon patch.
12. Integration proceeds with aligned artifacts.
```

**What COLLIDER does differently:**
- Surfaces `customer_identity` ambiguity **before** implementation begins.
- Detects and repairs `credit_amount` → `refund_amount` drift from source evidence.
- Protects the `money_representation` inference — flags it as INFERRED, does not
  treat consensus as proof.
- Preserves the Notifications workstream — no unnecessary rerun.
- Recognizes the success-response difference as semantically equivalent —
  no false alarm raised.
- Asks **exactly one** human question for the entire fixture.

---

## Part 2 — Interpretation Objects

The following JSON objects conform to
[`schemas/interpretation.schema.json`](../../schemas/interpretation.schema.json).
All objects use the schema-canonical field names: `value` for the interpreted
value and `consumed_by` for downstream consumers. The fields `explicit_in_source`
and `implementation_artifact` are additional properties not defined in the schema
but not forbidden by it; they carry fixture documentation context.

---

### 2A — `customer_identity` Interpretations

`customer_identity` is a concept held by **API and Ledger only**. Notifications
does not hold this concept — it holds `notification_contact` as a separate
concept in its own scope. The reconciler will not group Notifications under the
`customer_identity` disagreement.

#### API Workstream

```json
{
  "agent_id": "agent-api-001",
  "workstream": "api",
  "claims": [
    {
      "concept": "customer_identity",
      "value": "account_id",
      "epistemic_state": "UNKNOWN",
      "evidence_refs": [
        "BRIEF.md §Product Brief: 'credit the customer' — does not specify identity field",
        "BRIEF.md §Source Document: API Contract Stub — no customer identity field named"
      ],
      "evidence_relation": "UNAVAILABLE",
      "consumed_by": ["ledger"],
      "artifact_refs": ["api/handlers/recover.py — customer lookup field"]
    }
  ]
}
```

**Rationale:** The API workstream must look up the customer to trigger the credit.
It has no source guidance on which field identifies the customer. It defaults to
`account_id` as a plausible stable identifier. Epistemic state is `UNKNOWN`
because two plausible alternatives exist with no source evidence to distinguish
them. `consumed_by` is `["ledger"]` — Notifications is not a consumer of this
decision.

---

#### Ledger Workstream

```json
{
  "agent_id": "agent-ledger-001",
  "workstream": "ledger",
  "claims": [
    {
      "concept": "customer_identity",
      "value": "email",
      "epistemic_state": "UNKNOWN",
      "evidence_refs": [
        "BRIEF.md §Product Brief: 'credit the customer' — no identity field specified",
        "BRIEF.md §Source Document: API Contract Stub — notification_contact present but not a credit key"
      ],
      "evidence_relation": "UNAVAILABLE",
      "consumed_by": ["api"],
      "artifact_refs": ["ledger/credit_entry.py — customer lookup key"]
    }
  ]
}
```

**Rationale:** The Ledger workstream keys credit entries to customers and must
choose an identity field. It defaults to `email` as the commonly available
customer attribute. Epistemic state is `UNKNOWN` — no source evidence decides
this. Note: a poorly scoped Ledger agent might infer `email` from `notification_contact`,
but this is itself an inference error (confusing delivery address with credit
identity). The fixture does not require Ledger to make this error — only that it
independently chooses a different value than API.

---

#### Notifications Workstream — `notification_contact`

Notifications does **not** emit a `customer_identity` claim. It emits a separate
`notification_contact` claim for its own delivery address concern.

```json
{
  "agent_id": "agent-notifications-001",
  "workstream": "notifications",
  "claims": [
    {
      "concept": "notification_contact",
      "value": "email_address",
      "epistemic_state": "INFERRED",
      "evidence_refs": [
        "BRIEF.md §Source Document: API Contract Stub — notification_contact: string (type only, channel unspecified)",
        "BRIEF.md §Product Brief: 'notify them' — no channel specified"
      ],
      "evidence_relation": "INFERRED",
      "consumed_by": [],
      "artifact_refs": ["notifications/send_credit_notice.py — delivery address field"]
    }
  ]
}
```

**Rationale:** Notifications receives `notification_contact` as an input field
and must decide what kind of contact address it expects. Email is a plausible
default but the stub does not specify the channel type. This is a local
Notifications concern — no other workstream depends on this choice. The concept
is not `customer_identity`; it is a separate delivery-address concept. This
independence is what makes Notifications structurally unaffected by the upstream
`customer_identity` SPEC_GAP.

---

### 2B — `money_representation` Interpretations (one per workstream)

#### API Workstream

```json
{
  "agent_id": "agent-api-001",
  "workstream": "api",
  "claims": [
    {
      "concept": "money_representation",
      "value": "integer_cents",
      "epistemic_state": "INFERRED",
      "evidence_refs": [
        "BRIEF.md §Source Document: 'refund_amount': 'integer' — type is integer, unit unspecified",
        "Industry convention: monetary APIs commonly represent amounts as integer cents to avoid floating-point errors"
      ],
      "explicit_in_source": false,
      "consumed_by": ["ledger", "notifications"],
      "implementation_artifact": "POST /charges/{charge_id}/recover — refund_amount validation, expects integer >= 0"
    }
  ]
}
```

---

#### Ledger Workstream

```json
{
  "agent_id": "agent-ledger-001",
  "workstream": "ledger",
  "claims": [
    {
      "concept": "money_representation",
      "value": "integer_cents",
      "epistemic_state": "INFERRED",
      "evidence_refs": [
        "BRIEF.md §Source Document: 'refund_amount': 'integer' — consistent with cents, not proven",
        "Ledger convention: double-entry systems typically store monetary values as integer minor units"
      ],
      "explicit_in_source": false,
      "consumed_by": ["api"],
      "implementation_artifact": "ledger/credit_entry.py — amount column type INTEGER, comment: 'stored as cents'"
    }
  ]
}
```

---

#### Notifications Workstream

```json
{
  "agent_id": "agent-notifications-001",
  "workstream": "notifications",
  "claims": [
    {
      "concept": "money_representation",
      "value": "integer_cents",
      "epistemic_state": "INFERRED",
      "evidence_refs": [
        "BRIEF.md §Source Document: 'refund_amount': 'integer' — integer type assumed to be cents for display formatting",
        "Display logic: amount divided by 100 before rendering to user-facing message"
      ],
      "evidence_relation": "INFERRED",
      "consumed_by": [],
      "artifact_refs": ["notifications/send_credit_notice.py — format_amount(refund_amount / 100)"]
    }
  ]
}
```

**Shared inference note:** All three workstreams independently arrive at
`integer_cents`. COLLIDER must record this as `INFERRED` with consensus `true`
and must **not** upgrade the epistemic state to `OBSERVED`. The shared assumption
remains a latent risk until a human confirms it.

---

## Part 3 — Metrics

Both runs must record the following metrics. Measurement happens at the point
each run reaches integration-ready state (all three workstreams aligned, no open
contradictions).

### Required Metrics

| Metric                               | Definition                                                                                           | Measured at             |
|--------------------------------------|------------------------------------------------------------------------------------------------------|-------------------------|
| `human_clarifications_required`      | Number of questions the engineer answered about ambiguity in the brief                               | End of run              |
| `rework_cycles`                      | Number of workstream reimplementations triggered by a discovered disagreement                        | End of run              |
| `workstreams_rerun`                  | List of workstream IDs that were rerun after initial implementation                                  | End of run              |
| `contradictions_surfaced_pre_integration` | Number of cross-boundary contradictions found **before** integration (not during or after)      | Pre-integration gate    |
| `contradictions_surfaced_post_integration` | Number of cross-boundary contradictions found **during or after** integration                  | Integration gate onward |
| `time_to_integration_ready_minutes`  | Elapsed wall-clock minutes from brief receipt to integration-ready state                             | Timestamps              |
| `unaffected_workstreams_preserved`   | Count of workstreams correctly identified as unaffected and not rerun                                | End of run              |
| `false_positive_spec_gaps`           | SPEC_GAPs raised that EXPECTED-TRUTH.md marks as OUT_OF_SCOPE or non-gap                            | COLLIDER run only       |
| `false_negative_spec_gaps`           | TRUE SPEC_GAPs in EXPECTED-TRUTH.md that COLLIDER did not surface                                   | COLLIDER run only       |
| `agent_drifts_auto_repaired`         | AGENT_DRIFTs repaired from source evidence without requiring human input                             | COLLIDER run only       |

---

## Part 4 — Fair Measurement Rules

### Rule 1 — Same brief, same agents
Both runs receive **identical input**: the verbatim brief from BRIEF.md and the
same three workstream assignments. No additional context may be provided to either
run.

### Rule 2 — No oracle leakage
The baseline run agents must not have access to EXPECTED-TRUTH.md or this
BASELINE-CONTRACT.md. The COLLIDER run agents may have access to the structured
interpretation schema but not to the expected verdicts.

### Rule 3 — Record failures honestly
Both runs must record failures and unexpected outputs. A run that omits failures
to improve its metrics is invalid. See [`demo/CANONICAL-RUN.md`](../../demo/CANONICAL-RUN.md):
"Do not replace this file with a polished success narrative."

### Rule 4 — Baseline sets the comparison floor
Metrics are reported as **delta from baseline**. If COLLIDER produces more
rework cycles than the baseline in a given run, that must be reported as a
regression, not suppressed.

### Rule 5 — Correct abstention counts as a pass
If COLLIDER returns `UNKNOWN` and does not auto-resolve `customer_identity`, that
is recorded as `contradictions_surfaced_pre_integration += 1` and
`human_clarifications_required += 1`. This is the correct behavior and improves
the COLLIDER score relative to a baseline that silently proceeds with a wrong
identity field.

### Rule 6 — Notifications rerun is a false positive
If either run reruns the Notifications workstream after `customer_identity` is
resolved, that rerun is counted as a wasted cycle and reflected in `rework_cycles`
and the `unaffected_workstreams_preserved` metric.

### Rule 7 — Out-of-scope fields must not inflate disagreement counts
Internal response body fields (e.g. `{"status": "credited"}` vs `{"ok": true}`)
are not stub-defined cross-boundary fields and must not appear in either run's
`contradictions_surfaced_pre_integration` count. If COLLIDER raises an internal
body field as a cross-boundary disagreement, it is counted as
`false_positive_spec_gaps += 1`. The scope rule (only stub-defined fields are
candidates) eliminates this deterministically without semantic judgment.

---

## Part 5 — Expected Metric Comparison (predictive, not preset)

The following table predicts the directional outcome. Actual numbers must be
filled in from observed runs.

| Metric                                    | Baseline (predicted) | COLLIDER (predicted) | Observed Baseline | Observed COLLIDER |
|-------------------------------------------|---------------------|---------------------|-------------------|-------------------|
| `human_clarifications_required`           | 0–3 (ad hoc)        | exactly 1           | TBD               | TBD               |
| `rework_cycles`                           | 2–4                 | 0–1                 | TBD               | TBD               |
| `workstreams_rerun`                       | all 3 possible      | [api, ledger] only  | TBD               | TBD               |
| `contradictions_surfaced_pre_integration` | 0                   | 2 (gap + drift)     | TBD               | TBD               |
| `contradictions_surfaced_post_integration`| 2+                  | 0                   | TBD               | TBD               |
| `unaffected_workstreams_preserved`        | 0 (not tracked)     | 1 (notifications)   | TBD               | TBD               |
| `false_positive_spec_gaps`                | N/A                 | 0 (target)          | N/A               | TBD               |
| `false_negative_spec_gaps`                | N/A                 | 0 (target)          | N/A               | TBD               |

> **Do not preset improvement percentages.** Fill in observed columns after runs
> complete. Directional predictions are hypotheses, not claims.
