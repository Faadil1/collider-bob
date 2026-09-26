# Evidence Incident — overwritten local-abstain-001

Date: 2026-09-26

## What happened

The first execution of `local-abstain-001` returned a fixture verification
failure for Claim D:

- `notifications action=MISSING`
- `consumed_concept=MISSING`
- overall result: `FIXTURE FAILURES PRESENT`

The runtime behavior was correct: without a human decision there was no canon
patch and therefore no impact routing. The verifier incorrectly treated the
resolved-only Claim D as applicable to the abstention path.

The verifier was corrected so Claim D is tri-state. On the abstention path it is
`NOT_APPLICABLE`; on the resolved path it is evaluated as `PASS` or `FAIL`.

## Integrity limitation

The corrected run reused the same `local-abstain-001` directory, so the original
failed run artifacts were overwritten. They cannot truthfully be claimed as
immutably preserved.

The contemporaneous IBM Bob task transcript retains the historical failure and
diagnosis.

This incident caused the runtime to adopt a hard no-overwrite rule for evidence
directories. Canonical evidence runs must always use new run IDs and must never
use `--force`.

## Other failures observed during development

Behavioral testing also exposed failures after the API identity repair because
some API tests originally supplied only `customer_email`. The tests were
corrected to validate behavior while supplying both candidate identity values.
The final pre-canonical suite passed after that correction.

Real failure > fake success.

## Evidence-hardening regression discovered

After adding automatic baseline restoration, the full suite produced one
failure:

`TestFullPipeline.test_api_implementation_repaired`

The old test expected `api/handlers/recover.py` to remain permanently changed
to `account_id` after the pipeline returned. That expectation became invalid
once evidence capture correctly restored the baseline implementation.

The runtime behavior was not weakened. The test was replaced with assertions
over `artifact-hashes.json`, `repair.patch`, and baseline restoration.

This failure was retained as development evidence rather than hidden.
