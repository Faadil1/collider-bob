# COLLIDER — 100-Second Actual Product Demo

Status: SUPERSEDED FOR RECORDING by demo/DEMO-SCRIPT-ACTIVE.md (this script
predates ACTIVE MODE and the three-verdict guard; kept as the compression record).

Purpose: satisfy the hackathon requirement for at least 90 seconds of actual
product while maximizing judge comprehension.

## Judge Memory Sentence

**Three agents can be individually right and still reveal that the specification forgot to decide.**

## Signature Behavior

Independent implementation disagreements become probes for missing specification decisions.

## Signature Moment

**Everything is green locally. Integration still fails. COLLIDER discovers that
one mismatch is an agent mistake — and the other is a decision the specification
never made.**

---

## 0–10s — Show the brief

On screen:

`After a failed charge, credit the customer and notify them.`

Show the three workstreams:

- API
- Ledger
- Notifications

Narration:

> One short specification. Three independent implementation workstreams.

Do not explain architecture yet.

---

## 10–24s — Everything is green locally

Show baseline evidence:

- `30 local tests passed`
- `3/3 workstream suites green`

Then reveal:

`INTEGRATION_BLOCKED`

`2 conflicts`

Display:

`email != account_id`

`refund_amount != credit_amount`

Narration:

> All 30 local tests pass. But when the workstreams meet, they have built two
> incompatible assumptions.

Pause briefly on the contradiction.

---

## 24–43s — COLLIDER separates two different causes

Show classification output.

First:

`field_name`

`AGENT_DRIFT`

Evidence:

`BRIEF → refund_amount`

Ledger:

`credit_amount`

Narration:

> This mismatch is easy. The specification explicitly says refund_amount.
> Ledger drifted from the source.

Then show:

`customer_identity`

API → `email`

Ledger → `account_id`

`SPEC_GAP`

`UNKNOWN`

Narration:

> But this one is different. Neither agent violated the specification.
> The specification never chose an identity field.

This is the key conceptual moment.

---

## 43–55s — Correct abstention

Show:

`auto_resolve: false`

and the minimal clarification:

`Which field should identify the customer at the API/Ledger boundary?`

Narration:

> COLLIDER refuses to invent the answer. It asks one question.

Human decision shown:

`account_id`

Truth label visible:

`PRESEEDED HUMAN DECISION — LOCAL EVIDENCE`

Do not imply this was live interactive Bob input.

---

## 55–75s — Two targeted repair paths

Show Ledger repair:

`credit_amount → refund_amount`

badge:

`AGENT_DRIFT_EVIDENCE`

Then API repair:

`email → account_id`

badge:

`CANON_PATCH`

Keep Notifications visible with:

`UNCHANGED`

Narration:

> Source evidence repairs the agent mistake. The human decision repairs only the
> implementation that depended on the missing specification decision.
> Notifications is untouched.

---

## 75–90s — Integration proof

Show the executable integration receipt.

Before:

`2 conflicts`

`INTEGRATION_BLOCKED`

After:

`0 conflicts`

`INTEGRATION_READY`

Narration:

> Same starting workstream artifacts. Two conflicts before COLLIDER. Zero after
> the targeted repairs.

---

## 90–100s — Evidence / trust close

Flash:

- byte-identical starting workstream hashes
- repair.patch
- baseline restored
- `102 tests passed`

Then display truth boundary:

`LOCAL / PRESEEDED`

`LIVE_BOB GENERATION NOT CLAIMED`

Narration:

> Every claim is bound to committed evidence. The demo is local and preseeded;
> we do not claim live Bob generation that we did not observe.

Final screen:

**COLLIDER**

**Find the decision the specification forgot to make.**

---

## Recording rules

The actual-product segment should run approximately **100–110 seconds**, not
exactly 90 seconds, leaving safety margin above the 90-second requirement.

Never narrate:

- percentage improvement
- time savings
- production-scale proof
- PRESEEDED interpretations as LIVE_BOB
- Mars Climate Orbiter as something COLLIDER would have prevented

Do narrate:

- locally green
- two integration mismatches
- AGENT_DRIFT versus SPEC_GAP
- UNKNOWN / refusal to invent canon
- one human clarification
- two targeted executable repairs
- Notifications unchanged
- zero final integration conflicts
- evidence provenance
