# Public Session Isolation Proof — 2026-09-27

## Scope

User-recorded production smoke against:

https://collider-semantic-ci.faadil-casecraft.workers.dev/

The recording shows two browser contexts:

- an existing normal Edge session containing a completed guard flow;
- a newly opened Edge InPrivate context.

## Observed sequence

In the normal browser context, the existing COLLIDER session had already executed
the guard flow and showed the restored/ready state after a DECISION_REQUIRED
future-change probe.

A new InPrivate browser context was then opened and navigated to the same public
URL.

The new InPrivate context did **not** inherit the prior session's decision state.
It started from the fresh baseline and exposed the unresolved customer-identity
decision:

- initial detect state with 2 integration conflicts;
- DECISION_REQUIRED / human decision screen;
- API candidate = email;
- Ledger candidate = account_id;
- source = silent.

The InPrivate session could then independently run its own decision/guard flow.

## What this proves

- A fresh browser privacy context receives an independent COLLIDER session.
- Decision/guard state from the pre-existing normal browser context is not
  inherited by the new InPrivate context.
- Per-browser-session isolation is functioning on the public Cloudflare runtime.

## Truth boundary

This receipt proves browser-session isolation, not user/account isolation across
arbitrary devices or Cloudflare infrastructure failure scenarios.

Still pending for final Public Runtime / Ship closure:

- public mobile smoke;
- live x-collider-worker-version matched to Workers Builds commit;
- live page-header/CSP confirmation;
- external Real-User / Outsider Break Test.
