# Pre-Launch / Ship Assurance Gate

## Promotion chain

`PRE_LAUNCH_CODE_OK → DEPLOY → LIVE_RUNTIME_CHECK → CRITICAL_PATH_PASS → PROOF_CAPTURED → SHIP`

This gate applies to the real production runtime. Repository correctness alone is insufficient.

## Current deployment

- URL: https://collider-semantic-ci.faadil-casecraft.workers.dev/
- Runtime: Cloudflare Worker + Static Assets + per-browser-session Container
- Runtime code commit used for deployment: `bdfd9d35054ddefe8e48c7e67f525f5d3d55f5e7`
- Cloudflare version observed in deployment history: `f946793b`
- Active provenance: `CLOUDFLARE_CONTAINER / PRESEEDED / INTERACTIVE_WEB`
- Fresh LIVE_BOB generation: **NOT CLAIMED**

## Audit

Status as of commit `6564720` (escalated build: three guard verdicts). Rows
marked *(live)* were proven on the public runtime for `bdfd9d3` and must be
re-observed on the escalated build.

| Area | Status | Current evidence / remaining work |
|---|---|---|
| Legal & Privacy | N/A / REVIEWED | No accounts, no intended PII; opaque random session id only. No compliance claim. |
| HTTPS | PROVEN *(live)* | Served over HTTPS by Cloudflare. |
| Secrets | PROVEN FOR REPO | No application secret; tests assert none in wrangler.jsonc or the frontend. |
| Session safety | PROVEN IN CODE / RUNTIME PARTIAL | 256-bit opaque id, HttpOnly/Secure/SameSite=Lax, malformed or duplicate cookie replaced, container name hashed at the Worker. Live two-session isolation still to observe. |
| Request boundary | PROVEN IN CODE | Four allow-listed routes, 4 KiB bodies, only content-type/accept forwarded, probe id is an enum. |
| Container network | PROVEN IN CONFIG | `enableInternet = false`. |
| Security headers / CSP | PROVEN LOCALLY | demo-ui/_headers: `default-src 'none'`, same-origin script/style/connect, no inline, `frame-ancestors 'none'`, nosniff, no-referrer, DENY, COOP, Permissions-Policy. Worker adds nosniff + `default-src 'none'` CSP to every API response. Browser runs at three viewports: zero CSP violations. Live header read pending. |
| Abuse / rate limiting | ACCEPTED WITH BOUNDS | No dedicated rate limiter. Bounded by `max_instances = 20`, body cap, route allowlist, 24 decision runs per container (HTTP 429), one run per guard probe. |
| Metadata | PASS | Title, description, viewport, favicon (SVG). |
| Canonical / OG | N/A | Not needed for a judged single-purpose demo. |
| sitemap.xml | N/A | Search indexing is not a product requirement. |
| robots.txt | REVIEWED | Cloudflare-served; no indexing claim. |
| Accessibility | PARTIAL_PASS | Reduced-motion path skips staged reveals; future-change list uses real buttons with focus-visible outlines; mode switch is a radiogroup. No formal audit. |
| Performance | PARTIAL_PASS | Static assets only, no external fonts or scripts. Each guard probe runs the test suite server-side (seconds). No Core Web Vitals recorded. |
| Responsive / mobile | PROVEN LOCALLY | 390×844: no horizontal overflow, full flow incl. three verdicts. Live mobile smoke pending. |
| Error / loading / empty states | PASS | Unavailable runtime, action failure, 409 re-run, 429 cap, 503 container unreachable, abstention, judging and restore states. |
| Input/action safety | PROVEN | Mutations only in the session's compiled workspace; every probe restores exact bytes (sha256 checked). |
| Retry / idempotency | PASS FOR PROBES | A probe re-run returns 409; the UI re-shows the recorded receipt. Decisions create new isolated runs. |
| Observability | PARTIAL_PASS | Cloudflare observability on; one-line container request logs without bodies; Worker Version id on every API response. No alerting. |
| Analytics events | N/A | No product-analytics requirement. |
| Narrative / primary CTA | PARTIAL_PASS | demo/DEMO-SCRIPT-ACTIVE.md; outsider test pending. |
| Critical resolved path | PROVEN *(live)* + LOCAL | DECISION_REQUIRED → USE account_id → 2→0 → SEMANTICALLY_READY. |
| Negative path | PROVEN *(live)* + LOCAL | KEEP UNKNOWN; and MERGE_ALLOWED as false-positive control (local + container image). |
| Second act | PROVEN LOCAL + CONTAINER IMAGE | MERGE_BLOCKED / MERGE_ALLOWED / DECISION_REQUIRED, exact restore each time. Live pending. |
| Session isolation | PROVEN IN CODE | Two-instance container isolation proven earlier; live two-browser proof pending. |
| Runtime / commit binding | MECHANISM SHIPPED | `x-collider-worker-version` on every API response, shown in PROOF → PROVENANCE. |
| Rollback / deployment recovery | DOCUMENTED | cloudflare/README.md §Rollback / recovery. Not rehearsed. |
| Proof capture | PARTIAL_PASS | Local screenshots of all states; live capture pending. |

## Discoverability observation

A production fetch confirmed:

- title: `COLLIDER — Semantic CI`
- description: `Semantic CI for agentic software development: detect, decide, compile, patch, verify, remember, guard.`
- viewport is mobile-aware.
- `sitemap.xml` currently returns 404; classified N/A for this single-purpose demo.

## Ship blockers

1. Observe the escalated build live: three guard verdicts on the public URL.
2. Read `x-collider-worker-version` live and match it to the Workers Builds commit.
3. Two separate browser sessions each start at DECISION_REQUIRED.
4. Mobile smoke on the public URL.
5. Read live page headers and confirm the CSP from demo-ui/_headers is served.

## Gate verdict

**ACTIVE — PRE_LAUNCH_CODE_OK; LIVE_RUNTIME_CHECK PENDING; SHIP NOT YET EARNED**
