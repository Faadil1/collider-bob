# Transient Repair Module-Cache Contamination

Date: 2026-09-26

## Observed failure

After `local-resolved-003` appeared successful and restored its source files,
the complete in-process test suite produced three failures:

- baseline integration probe observed 1 conflict instead of 2
- Ledger response lookup raised `KeyError: credit_amount`
- Ledger response contained `refund_amount` while the imported baseline
  `CREDIT_FIELD_NAME` still reported `credit_amount`

The source file on disk had correctly returned to:

`CREDIT_FIELD_NAME = "credit_amount"`

## Cause boundary

The evidence pipeline temporarily rewrote Ledger to `refund_amount` and used
module reloads while capturing integration evidence. This allowed transient
module/bytecode state to outlive the repaired source state inside the parent
Python test process.

Therefore `local-resolved-003` is not promoted as canonical comparative
evidence even though its own receipts reported successful restoration.

## Correction

- integration probing now executes current source in isolated namespaces
- transient workstream modules are no longer reloaded into the shared process
- workstream bytecode caches are purged before behavioral subprocess tests
- bytecode caches are purged again after source restoration
- regression tests verify that the Ledger module remains baseline-clean and
  that the no-COLLIDER baseline still observes both conflicts afterward

A new canonical run is required.

Real failure > fake success.

## First mitigation was insufficient

The first correction isolated the integration probe from imports and purged
workstream bytecode caches before/after transient repair.

The next full-suite verification still failed:

- 99 tests passed
- 3 tests failed
- baseline probe observed 1 conflict instead of 2
- `ledger.CREDIT_FIELD_NAME` reported `refund_amount` inside the parent process
- Ledger baseline behavior was therefore still contaminated

This established that bytecode invalidation alone was insufficient. An
already-loaded module object in `sys.modules` can retain transient runtime state
even after the underlying source file has been restored.

## Final mitigation

After restoring source files, COLLIDER now:

1. purges workstream bytecode
2. finds any already-loaded workstream module objects
3. clears their executable namespace while preserving import metadata
4. executes the restored source directly into those existing namespaces
5. avoids `importlib.reload()` for transient repair synchronization

This explicitly restores both disk state and parent-process Python state.

A new canonical run remains required. `local-resolved-003` remains invalid for
promotion as comparative evidence.
