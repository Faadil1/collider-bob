# Fixture Brief — Failed Payment Recovery

## Product Brief (canonical source text)

> After a failed charge, credit the customer and notify them.

This is the **complete and verbatim product brief**. Nothing outside this sentence
is authoritative. All workstream decisions must trace back to it or be classified
as inferred / unknown.

---

## Workstream Assignments and Bounded Scope

Each workstream has a distinct local responsibility. The scope boundary is genuine,
not manufactured to produce divergence.

| Workstream    | Responsibility                                                              | Identity concern |
|---------------|-----------------------------------------------------------------------------|------------------|
| API           | HTTP endpoint: accept a failed-charge event, look up the customer, trigger the credit | Which field identifies the customer for credit lookup |
| Ledger        | Double-entry record: post a credit entry against a customer account          | Which field keys the credit entry to the correct account |
| Notifications | Outbound message: deliver a notification to the customer's contact address  | Which address to deliver to (email / phone / push) |

The **customer_identity** question (email vs account_id) is a cross-boundary concern
for API and Ledger: they must agree on which field keys a credit record to a customer.

The **notification_contact** question (which address to send to) is a separate local
concern for Notifications: it receives a contact address as input and does not need
to know how the upstream resolved customer identity for credit purposes.

These are **genuinely distinct concerns**. Notifications is not a stakeholder in the
`customer_identity` decision. Its independence is structural, not manufactured.

---

## Source Document: API Contract Stub

The following stub is **explicitly part of the source material** and is referenced
by all three workstreams.

```json
{
  "endpoint": "POST /charges/{charge_id}/recover",
  "request_body": {
    "charge_id": "string",
    "refund_amount": "integer",
    "notification_contact": "string"
  },
  "response": {
    "status": 200,
    "body": {
      "status": "credited"
    }
  }
}
```

> **Note on `refund_amount`:** the field name `refund_amount` appears verbatim in
> this stub. It is the explicit, authoritative name for the money field across all
> workstream boundaries. Any workstream that uses a different field name for this
> value contradicts the source document.

> **Note on `notification_contact`:** the stub defines `notification_contact` as
> the delivery address passed to the Notifications workstream. It is the value the
> caller resolves and passes in. Notifications consumes this field; it does not
> derive customer identity from it. The stub does not specify what type of address
> `notification_contact` contains (email, phone, push token) — that is a local
> Notifications concern.

> **Note on HTTP status:** the stub specifies `"status": 200` as the cross-boundary
> contract. The internal response body (`{"status": "credited"}`) is the API
> service's own acknowledgment format. Internal response body schemas are not
> cross-boundary contracts between workstreams.

---

## Deliberately Undecided Questions (fixture design notes)

The following questions are **intentionally left unanswered by the brief**. They
are not artificial ambiguities — each reflects a genuine design decision the brief
omits.

### Q1 — Durable Customer Identity (`customer_identity`)

The brief says "credit the customer." It does not specify:

- Whether the customer's durable cross-boundary identity field is their **email
  address** or their **account_id**.
- Which field the API and Ledger should use as the shared key.
- Whether both values are available in the failed-charge event payload.

**Scope:** API and Ledger only. Notifications receives `notification_contact` as a
separate pre-resolved input and is **not** a party to this decision. Conflating
notification delivery address with credit identity is itself an error.

This is a **TRUE SPEC_GAP**. API and Ledger will independently choose a value, and
neither can cite source evidence for their choice. A human must decide.

### Q2 — Money Representation (`money_representation`)

The brief says "credit the customer" and the API stub says `"refund_amount":
"integer"`. It does not specify:

- Whether `integer` means **integer cents** (e.g. `1000` = $10.00) or some other
  integer encoding.
- What currency is assumed.
- What rounding rules apply to fractional amounts.

All three workstreams are expected to independently assume integer cents. That
shared assumption is **INFERRED**, not observed — the brief never says "cents."

### Q3 — Notification Contact Type (`notification_contact_type`)

The stub includes `notification_contact: string` but does not specify:

- Whether this is an email address, phone number, push notification token, or other
  delivery channel.

This is a **local Notifications concern**, not a cross-boundary gap. Notifications
must make an assumption, but no other workstream depends on it. It will manifest
as a SHARED_INFERRED (or UNKNOWN) within Notifications only — not a cross-boundary
SPEC_GAP.

---

## Explicit Constraints (must be obeyed by all workstreams)

1. The field name for the money value at all cross-boundary interfaces **must** be
   `refund_amount` — this is stated in the API contract stub above.
2. The Notifications workstream receives `notification_contact` as its delivery
   address input. It does **not** own or resolve customer identity.
3. The HTTP success response from the API endpoint **must** return HTTP status `200`.
4. Internal response body schemas (e.g. `{"status":"credited"}`, `{"ok":true}`) are
   **not** cross-boundary contracts. Only HTTP status codes are shared interface
   contracts between workstreams.

---

## Negative Control: Internal Response Body Schemas Are Out of Scope

The API endpoint returns `{"status": "credited"}` on success (HTTP 200).
The Notifications service returns `{"ok": true}` on success (HTTP 200).

These are **internal response body formats** for each service's own clients. They
are not a shared cross-boundary field. The API contract stub specifies only
`"status": 200` as the cross-boundary contract — not the body content.

COLLIDER's scope rule: **only fields defined in the shared contract stub are
candidates for cross-boundary disagreement classification**. `notification_contact`
and `refund_amount` are in the stub. Internal body keys (`status`, `ok`) are not.

This rule is deterministic: it is derived from the stub's field list, not from a
model judgment about whether two responses "mean the same thing."

---

## Fixture Inventory

| Label              | Concept                    | Scope              | Classification Target | Correct COLLIDER Verdict       |
|--------------------|----------------------------|--------------------|-----------------------|-------------------------------|
| A — TRUE SPEC_GAP  | `customer_identity`        | API, Ledger        | SPEC_GAP              | UNKNOWN → HUMAN DECISION       |
| B — AGENT_DRIFT    | `field_name` (money field) | All                | AGENT_DRIFT           | Repair Ledger to `refund_amount` |
| C — SHARED INFER.  | `money_representation`     | All                | INFERRED (all three)  | INFERRED, not auto-resolved    |
| D — UNAFFECTED WS  | Notifications isolation    | Structural         | No rerun needed       | Notifications has no `customer_identity` claim; impact router: unaffected |
| E — UNKNOWN PATH   | `customer_identity`        | API, Ledger        | UNKNOWN               | Abstain, surface to human      |
| F — NEGATIVE CTRL  | Internal response body     | Scoping rule       | Out of stub scope     | Not a cross-boundary contract; not classified |

---

## Prompt Isolation Design

Each workstream agent receives:

1. The verbatim product brief.
2. The API contract stub (above) — the shared source document.
3. Its own workstream scope description (from the table above) — local responsibility only.
4. The instruction to emit a structured interpretation object for every cross-boundary
   concept it encounters, with epistemic state and evidence references.

**What workstream prompts must NOT contain:**

- The expected answer for any concept.
- Instructions to use a specific value (e.g. "use email", "use account_id").
- Access to any other workstream's scope or interpretation.

The brief genuinely permits multiple interpretations of `customer_identity` because
it does not name an identity field. An API agent with local responsibility for "look
up the customer and trigger the credit" will reasonably consider multiple identity
strategies — and whichever it chooses will reflect a real local design decision, not
a fabricated one.
