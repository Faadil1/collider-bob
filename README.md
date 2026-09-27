# COLLIDER

> **Semantic CI for Agentic Software Development**  
> **Fuzz the specification. Repair the decision. Prove the system understands it.**

**Live demo:** https://collider-semantic-ci.faadil-casecraft.workers.dev/

Parallel AI coding agents can all be locally correct and still build incompatible
assumptions because the specification never made a cross-boundary decision.

COLLIDER turns disagreement into a specification probe:

```text
PROBE → COLLIDE → ADJUDICATE → DECIDE
      → COMPILE → PATCH → VERIFY → REMEMBER → GUARD
```

> **When AI agents disagree, COLLIDER finds the decision the specification forgot to make.**

## The 15-second proof

The canonical fixture starts with:

- **30 local tests passing**
- **3/3 workstreams locally green**
- **2 integration conflicts**

Two mismatches have different causes:

```text
refund_amount vs credit_amount
→ source explicitly says refund_amount
→ AGENT_DRIFT
→ repair from source evidence

email vs account_id
→ source never chooses a customer identity
→ SPEC_GAP / UNKNOWN
→ one human decision required
```

Selecting `account_id` compiles that decision into:

- a specification patch
- targeted code repairs
- a regression contract
- decision memory

The executable integration result moves from:

```text
2 conflicts / INTEGRATION_BLOCKED
→
0 conflicts / SEMANTICALLY_READY
```

## The second act: three Semantic CI verdicts

After the repair, COLLIDER tests controlled future changes against decision memory:

| Future change | Tests | Verdict |
|---|---:|---|
| API reverts `account_id → email` | 33 pass / 4 fail | **MERGE_BLOCKED** |
| Notification wording only | 37 pass | **MERGE_ALLOWED** |
| Ledger changes cents → dollars | **37 pass** | **DECISION_REQUIRED** |

The third row is the signature moment: **all tests pass, but COLLIDER still refuses
to merge because the workstreams now disagree where the source is silent.**

For the identity revert, the same changed tree without decision memory becomes
`DECISION_REQUIRED` instead of `MERGE_BLOCKED`. Memory changes the verdict.

Every guard probe restores the prior verified workspace exactly.

## Truth boundary

COLLIDER deliberately distinguishes evidence from inference:

```text
SOURCE EXPLICIT + AGENT DISAGREES
→ AGENT_DRIFT
→ evidence-grounded repair

SOURCE SILENT + AGENTS DISAGREE
→ SPEC_GAP
→ UNKNOWN
→ HUMAN DECISION REQUIRED

SOURCE SILENT + AGENTS AGREE
→ SHARED ASSUMPTION
→ INFERRED, never fact
```

The canonical interpretation objects are **PRESEEDED**. They are not claimed as
live Bob-generated outputs.

The future-change probes are controlled edits, not autonomous agents.

Fresh-agent replay exists as a contract, but is
**NOT_EXECUTED / PENDING_LIVE_BOB**.

## KEEP UNKNOWN is a valid result

COLLIDER does not force a decision.

`KEEP UNKNOWN`:

- writes no canon
- writes no decision memory
- applies no repair
- leaves the gate at `DECISION_REQUIRED`

Correct abstention is a product behavior, not an error state.

## IBM Bob 2.0

IBM Bob 2.0 was used directly in the repository as a load-bearing development
agent during implementation and refinement.

COLLIDER now also ships as a **project-native Bob capability**, not only as a
standalone runtime:

- `.bob/custom_modes.yaml` — **⚛️ COLLIDER Semantic CI** custom mode
- `.bob/skills/collider-semantic-review/SKILL.md` — reusable semantic-review skill
- `.bob/rules/collider-truth-boundary.md` — workspace truth/provenance rules
- `collider/bob_live.py` — rejects fake/relabelled LIVE_BOB inputs and binds real
  Bob session/task references to interpretation hashes
- `collider/bob_rules.py` — exports approved COLLIDER decision memory into Bob
  workspace rules so future Bob agents inherit semantic canon
- `.bob/mcp.json` + `collider/mcp_server.py` — a project-level **COLLIDER MCP
  server** that exposes semantic gate, PR gate, decision memory, LIVE_BOB
  validation, rule export, and replay evaluation as native Bob tools

The native live protocol uses **three isolated Bob subagents** as ambiguity
probes, validates their independent interpretation artifacts, then lets the same
COLLIDER pipeline classify, decide, compile, verify, remember, and guard.

The integration mechanism is shipped and tested. A real Bob session is still
required before a specific interpretation run may be called `LIVE_BOB`; the
repository deliberately refuses to relabel PRESEEDED evidence.

See:

- `submission/BOB-USAGE.md`
- `product/BOB-NATIVE-INTEGRATION.md`
- `evidence/bob-sessions/README.md`

## Real pull-request Semantic CI

COLLIDER is not only an interactive demo. The repository ships a real GitHub
pull-request gate in `.github/workflows/semantic-ci.yml`.

For every registered semantic concept changed by a PR, the gate compares the
new value against explicit source authority and committed decision memory:

```text
change conforms to source/canon
→ MERGE_ALLOWED

change violates source/canon
→ MERGE_BLOCKED / AGENT_DRIFT

change creates disagreement where source is silent
→ DECISION_REQUIRED / SPEC_GAP
```

The action posts the verdict directly on the PR, uploads a machine-readable
receipt, and blocks the merge for `MERGE_BLOCKED` or `DECISION_REQUIRED`.
It also reports the conventional workstream-test result beside the semantic
verdict so judges can see when ordinary tests stay green while Semantic CI
still requires a decision.

## Public runtime

The hosted demo runs on:

```text
Cloudflare Worker
├── Workers Static Assets → demo-ui/
└── /api/* → per-browser-session Cloudflare Container
    └── Python COLLIDER runtime
```

Production proof includes:

- public three-verdict guard
- exact workspace restoration
- separate browser-session isolation
- real-iPhone mobile smoke
- Worker-version ↔ Git-commit binding
- live CSP/security-header verification

Receipts are under `evidence/runtime/`.

## Run locally

```bash
python3 demo-ui/server.py
# open http://127.0.0.1:4173
```

Core CLI:

```bash
python3 -m collider.gate

python3 -m collider.decision_compiler \
  --value account_id \
  --decision-id demo-decision

python3 -m collider.guard_probe \
  --workspace .collider/workspaces/demo-decision \
  --out-dir .collider/runs/demo-decision \
  --probe IDENTITY_REVERT
```

## Verify

```bash
python3 -m pytest -q -p no:cacheprovider
npx tsc --noEmit
```

Last full recorded verification before submission packaging:

```text
255 passed
123 subtests passed
TypeScript: clean
```

The canonical test configuration excludes committed evidence from test collection
and writes transient test runs outside `evidence/`.

## Evidence

Key receipts:

- `evidence/runs/baseline-001/`
- `evidence/runs/local-resolved-004/`
- `evidence/comparisons/baseline-001-vs-local-resolved-004.md`
- `evidence/runtime/PUBLIC-THREE-VERDICT-GUARD-2026-09-27.md`
- `evidence/runtime/PUBLIC-SESSION-ISOLATION-2026-09-27.md`
- `evidence/runtime/PUBLIC-MOBILE-PROVENANCE-2026-09-27.md`
- `evidence/runtime/RUNTIME-COMMIT-BINDING-2026-09-27.md`
- `evidence/runtime/LIVE-CSP-HEADERS-2026-09-27.md`

## Repository map

```text
collider/       semantic gate, decision compiler, guard, replay contract
baseline/       no-COLLIDER executable control
fixtures/       canonical failed-payment fixture
evidence/       immutable comparison/runtime receipts
demo-ui/        interactive judge surface
demo/           recording script and demo contract
product/        PRD, truth boundary, architecture, gates
submission/     hackathon submission copy
state/          canonical CURRENT / HANDOVER
tests/          regression, integrity and deployment tests
cloudflare/     Worker/Container deployment adapter
```

## Submission status

| Gate | Status |
|---|---|
| Creative Depth & Distinctiveness | **PROVEN** |
| Truth Boundary / Negative Path / Evidence Integrity | **PROVEN** |
| Runtime / Commit Binding | **PROVEN** |
| Public Runtime / Live Proof | **PROVEN** |
| Deterministic Demo | **PROVEN** |
| Pre-Launch / Ship Assurance | **PROVEN** |
| Concept Compression | **PROVEN** with documented outsider-test waiver |
| Judge Performance Assurance | **PROVEN FOR DEMO LOCK** |
| Submission Integrity | **PENDING final media/package** |
| LIVE_BOB canonical interpretations | **NOT CLAIMED** |

Canonical status: `product/GATEWAY-REGISTRY.md`

## Real-world anchor

Mars Climate Orbiter is used only as evidence for the broader class of
cross-boundary assumption failures. COLLIDER does **not** claim it would have
prevented that historical incident.

See `product/PROBLEM-EVIDENCE.md` for sources and claim boundaries.

---

**Real failure > fake success.**

MIT licensed.
