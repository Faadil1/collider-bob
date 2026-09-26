# COLLIDER — Evidence Schema

## Purpose

The evidence schema defines the complete artifact structure for a COLLIDER run. Every claim
made in a demo or submission must map to a file in this schema. No claim is made without
a corresponding artifact. No artifact is deleted or modified to improve the appearance of
results. Failures are preserved.

---

## Run directory structure

```
evidence/runs/<run-id>/
  manifest.json
  interpretations/
    api.json
    ledger.json
    notifications.json
  classifications.json
  canon-patches/
    <concept>.json
  impact-set.json
  tests-before.txt
  tests-after.txt
  failures.json
  metrics.json
```

---

## `manifest.json`

Run-level metadata. Written at run start; finalized at run end.

```json
{
  "run_id": "<run-id>",
  "fixture_version": "<semver or git tag of the fixture being run>",
  "git_commit": "<SHA of the repository HEAD at run start>",
  "timestamp": "<ISO 8601 UTC timestamp of run start>",
  "run_type": "baseline | collider",
  "generation_mode": "LIVE_BOB | PRESEEDED | SIMULATED | LOCAL | LOCAL_STUB",
  "bob_session_ref": "<Bob session ID or null if generation_mode is not LIVE_BOB>",
  "test_command": "<exact command used to run integration tests>",
  "known_limitations": [
    "<free-text description of any known limitation, assumption, or caveat for this run>"
  ]
}
```

**Field notes:**

- `run_type`: `baseline` means the run executes the fixture without COLLIDER intervention.
  `collider` means the full classification, clarification, and repair loop was executed.
- `generation_mode`: **required; must be truthful**.
  - `LIVE_BOB` — interpretation objects were produced by live Bob parallel subagents in a
    real session. This is the canonical submission target.
  - `PRESEEDED` — interpretation objects were authored and committed before the run; the
    classifier and routing pipeline ran against them. Must be disclosed. Not a live run.
  - `SIMULATED` — the full pipeline was simulated without Bob. Not a live run.
  - `LOCAL` — run on local tooling without Bob session infrastructure.
  - `LOCAL_STUB` — one or more components were stubbed. Never narrate as LIVE_BOB.
- `bob_session_ref`: the Bob session reference when `generation_mode` is `LIVE_BOB`. Must
  be `null` for all other modes. Provides the audit trail linking the run to a real session.
- `known_limitations`: must be populated honestly. A `PRESEEDED` run with an empty
  `known_limitations` array is invalid.

---

## `interpretations/<workstream>.json`

One file per workstream. Records what the agent declared about each shared concept.

```json
{
  "agent_id": "<agent identifier>",
  "workstream": "api | ledger | notifications",
  "run_id": "<run-id>",
  "git_commit": "<SHA of the workstream's output at interpretation extraction time>",
  "timestamp": "<ISO 8601 UTC>",
  "generation_mode": "LIVE_BOB | PRESEEDED | SIMULATED | LOCAL | LOCAL_STUB",
  "claims": [
    {
      "concept": "<concept_name>",
      "value": "<the value the workstream used for this concept>",
      "epistemic_state": "OBSERVED | INFERRED | UNKNOWN",
      "evidence_refs": ["<file path and line, or description>"],
      "evidence_relation": "EXPLICIT | INFERRED | UNAVAILABLE | CONFLICTING",
      "consumed_by": ["<workstream_id>"],
      "artifact_refs": ["<file/function reference for the implementation decision>"]
    }
  ]
}
```

**Field notes:**

- `generation_mode`: aligns with the manifest field. Records whether this specific
  interpretation was produced live by a Bob agent or authored as a fixture. Must match
  manifest `generation_mode` for the run.
- `epistemic_state`: the epistemic state of the interpretation itself (not the classification
  result). `OBSERVED` requires a cited source passage. `INFERRED` means plausible but not
  explicitly specified. `UNKNOWN` means no basis could be determined.
- `evidence_refs`: list of source document citations supporting this interpretation. Must
  reference committed documents. `[]` is valid only if `epistemic_state` is `UNKNOWN`.
- `evidence_relation`: characterizes how the evidence supports the value.
  - `EXPLICIT` — source names this exact value as the requirement.
  - `INFERRED` — source is consistent with this value but does not name it.
  - `UNAVAILABLE` — no source evidence was found.
  - `CONFLICTING` — sources give contradictory signals.
- `consumed_by`: list of workstream IDs whose implementation depends on this value. Used
  by the impact router to determine repair scope after a canon patch. Must not include
  workstreams that do not genuinely consume the concept.
- `artifact_refs`: file/function references in the workstream's implementation where this
  decision is embodied. Provides a link from the interpretation claim to executable evidence.
- Do not use confidence scores as a substitute for evidence. If evidence is insufficient,
  set `epistemic_state: UNKNOWN` and `evidence_relation: UNAVAILABLE`.

**Fixture values (concepts by workstream):**

| Workstream | `customer_identity` | `field_name` | `money_representation` | `notification_contact` |
|------------|--------------------|--------------|-----------------------|------------------------|
| API | `email` | `refund_amount` | `integer_cents` | _(not applicable)_ |
| Ledger | `account_id` | `credit_amount` | `integer_cents` | _(not applicable)_ |
| Notifications | _(not applicable — different concept)_ | _(not applicable)_ | `integer_cents` | `email_address` |

Note: `customer_identity` is scoped to API and Ledger only. Notifications holds `notification_contact`
as a separate concept. Internal response body fields are out of cross-boundary scope (scope filter Step 0).

---

## `classifications.json`

Array of classification results, one per shared concept.

```json
[
  {
    "concept": "<concept_name>",
    "run_id": "<run-id>",
    "timestamp": "<ISO 8601 UTC>",
    "workstream_values": {
      "<workstream>": "<value>"
    },
    "normalized_values": {
      "<workstream>": "<normalized value after Step 1>"
    },
    "classification": "NO_DISAGREEMENT | AGENT_DRIFT | SPEC_GAP | UNKNOWN",
    "classification_subtype": "SHARED_INFERRED | NEGATIVE_CONTROL | null",
    "agent_drift_workstreams": ["<workstream>"],
    "source_evidence": {
      "document": "<file path or null>",
      "line": "<line number or null>",
      "excerpt": "<exact text or null>",
      "evidence_state": "OBSERVED | INFERRED | UNKNOWN"
    },
    "classifier_step_reached": 1,
    "classifier_judgment_used": true,
    "notes": "<free-text>"
  }
]
```

**Field notes:**

- `agent_drift_workstreams`: populated only when `classification` is `AGENT_DRIFT`. Lists
  the specific workstreams that contradicted the source evidence.
- `source_evidence`: the passage used in Step 3. Must be present for any `AGENT_DRIFT`
  classification. `null` fields are acceptable for `SPEC_GAP` (source was silent).
- `classifier_step_reached`: the Step (0–5) at which the algorithm terminated.
- `classifier_judgment_used`: `true` if Step 3 or Step 4 model judgment was involved.
  This is an honesty flag, not a quality flag. It means the classification is auditable
  but not purely algorithmic.

**Fixture expected values:**

| Concept | Scope | Classification | Subtype | `agent_drift_workstreams` |
|---------|-------|---------------|---------|---------------------------|
| `customer_identity` | api, ledger | `SPEC_GAP` | `null` | `[]` |
| `field_name` | api, ledger | `AGENT_DRIFT` | `null` | `["ledger"]` |
| `money_representation` | api, ledger, notifications | `NO_DISAGREEMENT` | `SHARED_INFERRED` | `[]` |
| Internal response bodies | N/A | `OUT_OF_SCOPE` | `NEGATIVE_CONTROL` | `[]` |

---

## `canon-patches/<concept>.json`

One file per resolved concept. Written only after a human decision is received.

```json
{
  "concept": "<concept_name>",
  "run_id": "<run-id>",
  "canonical_value": "<the decided value>",
  "decision_source": "human | evidence",
  "decided_by": "<identifier of the human or process that made the decision>",
  "timestamp": "<ISO 8601 UTC>",
  "git_commit": "<SHA at time of patch creation>",
  "evidence_state": "OBSERVED",
  "rationale": "<free-text: why this value was chosen>",
  "prior_classification": "SPEC_GAP | AGENT_DRIFT | UNKNOWN",
  "prior_state": "SPEC_GAP | UNKNOWN",
  "applies_to_run": "<run-id>"
}
```

**Field notes:**

- `evidence_state` is always `OBSERVED` for a committed canon patch, because the canon
  patch itself is the evidence. The human decision is the deciding act; once committed,
  it is observed fact for downstream consumers.
- `decision_source`: `human` means a human explicitly chose the value. `evidence` means
  the value was unambiguously specified in source material and the patch is recording an
  existing fact, not making a new decision.
- A canon patch must not be written for `UNKNOWN` classifications where the human answer
  was itself ambiguous. The patch file must not exist until a clear decision is received.

---

## `impact-set.json`

Records which workstreams are affected by each canon patch and what action was taken.

```json
{
  "run_id": "<run-id>",
  "timestamp": "<ISO 8601 UTC>",
  "canon_patch_commit": "<SHA>",
  "impacts": [
    {
      "concept": "<concept_name>",
      "canonical_value": "<value>",
      "workstream_impacts": [
        {
          "workstream": "<workstream>",
          "consumed_concept": true,
          "prior_value": "<what it used before>",
          "matches_canon": true,
          "action": "repair | preserve | not_applicable",
          "action_rationale": "<free-text>"
        }
      ]
    }
  ]
}
```

**Fixture expected values for `customer_identity` after canon patch (`account_id`):**

| Workstream | `consumed_concept` | `prior_value` | `matches_canon` | `action` | Rationale |
|------------|--------------------|---------------|-----------------|----------|-----------|
| API | `true` | `email` | `false` | `repair` | contradicts canon |
| Ledger | `true` | `account_id` | `true` | `preserve` | already canonical |
| Notifications | `false` | N/A | N/A | `not_applicable` | holds `notification_contact`, not `customer_identity`; no dependency |

---

## `tests-before.txt`

Raw output of the test command (`manifest.json → test_command`) run against the baseline
workstream outputs, before any COLLIDER repair. Stored verbatim.

**Expected state for the demo fixture:** each workstream's local tests pass in isolation.
This is the "everything looked green locally" moment. The file is not modified after the
fact. If tests fail in the baseline, that failure is preserved here and noted in `failures.json`.

Note: "local tests pass" means each workstream is internally self-consistent. It does not
mean cross-boundary semantic compatibility has been verified. That is what COLLIDER adds.

---

## `tests-after.txt`

Raw output of the test command run after COLLIDER repair. Stored verbatim.

**Expected state for the demo fixture:** each workstream's local tests still pass after
repair. If repair introduced new failures, they are preserved here and in `failures.json`.
The `tests-after.txt` file is never edited to remove failure output.

---

## `failures.json`

Preserved record of any test failures, classification errors, repair failures, or
ambiguous outcomes encountered during the run. Never erased.

```json
{
  "run_id": "<run-id>",
  "failures": [
    {
      "failure_type": "test_failure | classification_error | repair_failure | retrieval_failure | ambiguous_answer",
      "workstream": "<workstream or null>",
      "concept": "<concept or null>",
      "timestamp": "<ISO 8601 UTC>",
      "description": "<free-text description of what failed>",
      "severity": "critical | high | medium | low",
      "resolution": "resolved | unresolved | mitigated",
      "resolution_notes": "<free-text>"
    }
  ]
}
```

**Field notes:**

- An empty `failures` array is acceptable only if the run completed without any failure,
  error, or ambiguity. If anything went wrong and this array is empty, the evidence
  record is dishonest.
- `resolution` values: `resolved` means the failure was corrected and verified. `mitigated`
  means a workaround was applied. `unresolved` means the failure persists and is noted.
  Unresolved failures do not disqualify the run; they are part of the record.

---

## `metrics.json`

Observed metrics from the run. Contains only values that were directly measured. No
preset improvement claims. No before/after comparisons that were not actually run.

```json
{
  "run_id": "<run-id>",
  "timestamp": "<ISO 8601 UTC>",
  "metrics": [
    {
      "metric": "<metric name>",
      "value": "<observed value>",
      "unit": "<unit or null>",
      "measured_at": "<ISO 8601 UTC>",
      "evidence_state": "OBSERVED | INFERRED",
      "notes": "<free-text or null>"
    }
  ]
}
```

**Example metrics for the demo fixture:**

| Metric | Expected value | Unit | Notes |
|--------|---------------|------|-------|
| `disagreements_detected` | `2` | count | AGENT_DRIFT + SPEC_GAP |
| `shared_inferred_detected` | `1` | count | `money_representation` |
| `negative_controls_correct` | `1` | count | `success_response` → NO_DISAGREEMENT |
| `workstreams_repaired` | `1` | count | API only |
| `workstreams_preserved` | `2` | count | Ledger + Notifications |
| `canon_patches_written` | `1` | count | `customer_identity` |
| `unknown_returned` | `0` | count | All resolvable in this run |

**Constraint:** These values are written from observation, not preset. If the run produces
different numbers, those numbers are what gets written. The schema does not enforce expected
values.

---

## Schema versioning

This schema is versioned by the `fixture_version` field in `manifest.json`. If the schema
changes between runs, the `fixture_version` must change. Old run directories are preserved
as-is and are read using the schema version in their `manifest.json`.
