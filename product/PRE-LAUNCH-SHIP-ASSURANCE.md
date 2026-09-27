# Pre-Launch / Ship Assurance Gate

## Promotion chain

`PRE_LAUNCH_CODE_OK → DEPLOY → LIVE_RUNTIME_CHECK → CRITICAL_PATH_PASS → PROOF_CAPTURED → SHIP`

This gate applies to the real production runtime. Repository correctness alone is insufficient.

## Current deployment

- URL: https://collider-semantic-ci.faadil-casecraft.workers.dev/
- Runtime: Cloudflare Worker + Static Assets + per-browser-session Container
- Escalated three-verdict build: **OBSERVED LIVE**
- Public receipt: `evidence/runtime/PUBLIC-THREE-VERDICT-GUARD-2026-09-27.md`
- Active provenance: `CLOUDFLARE_CONTAINER / PRESEEDED / INTERACTIVE_WEB`
- Fresh LIVE_BOB generation: **NOT CLAIMED**
- Exact Workers version ↔ Git commit binding: **PENDING**

## Audit

| Area | Status | Current evidence / remaining work |
|---|---|---|
| Legal & Privacy | N/A / REVIEWED | No accounts, no intended PII; opaque random session id only. No compliance claim. |
| HTTPS | PROVEN LIVE | Served over HTTPS by Cloudflare. |
| Secrets | PROVEN FOR REPO | No application secret; tests assert none in wrangler.jsonc or the frontend. |
| Session safety | PROVEN LIVE | 256-bit opaque id, HttpOnly/Secure/SameSite=Lax, malformed or duplicate cookie replaced, container name hashed at the Worker; a fresh InPrivate context started independently at DECISION_REQUIRED instead of inheriting the resolved normal-browser session. |
| Request boundary | PROVEN IN CODE | Four allow-listed routes, 4 KiB bodies, only content-type/accept forwarded, probe id is an enum. |
| Container network | PROVEN IN CONFIG | `enableInternet = false`. |
| Security headers / CSP | PROVEN LOCALLY | demo-ui/_headers: strict same-origin CSP and hardening headers; browser runs at three viewports had zero CSP violations. Live header read still pending. |
| Abuse / rate limiting | ACCEPTED WITH BOUNDS | No dedicated rate limiter. Bounded by max_instances=20, body cap, route allowlist, 24 decision runs per container, one run per guard probe. |
| Metadata | PASS | Title, description, viewport, favicon. |
| Canonical / OG | N/A | Not needed for a judged single-purpose demo. |
| sitemap.xml | N/A | Search indexing is not a product requirement. |
| robots.txt | REVIEWED | Cloudflare-served; no indexing claim. |
| Accessibility | PARTIAL_PASS | Reduced-motion path, real buttons, focus-visible outlines, radiogroup mode switch. No formal audit. |
| Performance | PARTIAL_PASS | Static assets only, no external fonts/scripts. Guard probes execute test suite server-side. No Core Web Vitals recorded. |
| Responsive / mobile | PROVEN LOCALLY | 390×844 full flow with no horizontal overflow. Public mobile smoke pending. |
| Error / loading / empty states | PASS | Unavailable runtime, action failure, 409 re-run, 429 cap, 503 container unreachable, abstention, judging and restore states. |
| Input/action safety | PROVEN | Mutations only in session workspace; every probe restores exact bytes. |
| Retry / idempotency | PASS FOR PROBES | Probe re-run returns 409; UI re-shows recorded receipt. Decisions create new isolated runs. |
| Observability | PARTIAL_PASS | Cloudflare observability on; one-line request logs without bodies; Worker Version id emitted on API responses. No alerting. |
| Analytics events | N/A | No product-analytics requirement. |
| Narrative / primary CTA | PARTIAL_PASS | demo/DEMO-SCRIPT-ACTIVE.md; outsider test pending. |
| Critical resolved path | PROVEN LIVE | DECISION_REQUIRED → USE account_id → 2→0 → SEMANTICALLY_READY. |
| Negative path | PROVEN LIVE + LOCAL | KEEP UNKNOWN previously observed live; current escalated guard now also proves harmless change → MERGE_ALLOWED. |
| Second act | PROVEN LIVE | Public runtime visibly executed MERGE_BLOCKED / MERGE_ALLOWED / DECISION_REQUIRED with exact restore after each probe. Receipt: evidence/runtime/PUBLIC-THREE-VERDICT-GUARD-2026-09-27.md. |
| Session isolation | PROVEN LIVE | Normal browser session and fresh InPrivate context remained independent. Receipt: evidence/runtime/PUBLIC-SESSION-ISOLATION-2026-09-27.md. |
| Runtime / commit binding | MECHANISM SHIPPED | `x-collider-worker-version` on every API response, shown in PROOF → PROVENANCE. Live value still must be matched to Workers Builds commit. |
| Rollback / deployment recovery | DOCUMENTED | cloudflare/README.md §Rollback / recovery. Not rehearsed. |
| Proof capture | PARTIAL_PASS | Public desktop capture includes all three guard verdicts, restore, code diffs/hashes, plus separate-session isolation. Mobile/version/header receipts remain. |

## Public escalated-build observation

The production recording showed:

- **MERGE_BLOCKED** for reverting `customer_identity` to `email`
- same diff without memory → **DECISION_REQUIRED**
- **MERGE_ALLOWED** for a notification wording-only change
- same diff without memory → **DECISION_REQUIRED**
- **DECISION_REQUIRED** for changing Ledger money unit to decimal dollars
- all tests remain green on the money-unit probe
- exact-byte restoration after each probe
- `SEMANTICALLY READY AGAIN`
- regression contract `7 / 7`
- proof drawer with code-diff and hash/restoration evidence

## Ship blockers

1. Read `x-collider-worker-version` live and match it to the Workers Builds commit.
2. Mobile smoke on the public URL.
3. Read live page headers and confirm the CSP from demo-ui/_headers is served.

## Gate verdict

**ACTIVE — LIVE_RUNTIME_CHECK PARTIALLY PROVEN; CORE SECOND ACT PROVEN LIVE; SHIP NOT YET EARNED**
