# COLLIDER — Claude UI/UX Handoff — 2026-09-27

## Mission

Perform the **pre-final judge-facing UI/UX redesign** of COLLIDER before slides,
cover, and final video packaging.

This is **not** a product rearchitecture and **not** a semantic rewrite.

The product logic, evidence model, runtime behavior, Bob proof, truth boundaries,
and demo sequence are already locked and proven. Your job is to make the existing
product feel visually inevitable, distinctive, judge-readable, and native to the
name **COLLIDER**.

Work directly in `demo-ui/`.

## Current implementation

The public UI is vanilla HTML/CSS/JS:

- `demo-ui/index.html`
- `demo-ui/styles.css`
- `demo-ui/app.js`
- `demo-ui/loop-state.js`
- `demo-ui/evidence.json`

The public flow is:

`DETECT → DECIDE → COMPILE → PATCH → VERIFY → REMEMBER → GUARD`

A separate proof/evidence layer exists.

Do not introduce a framework, bundler, dependency-heavy design system, or a new
runtime architecture unless absolutely required. Prefer a disciplined redesign
inside the current static/runtime contract.

## Locked product truth

Do not change these semantics:

- category: **Semantic CI for Agentic Software Development**
- judge memory sentence:
  **“When AI agents disagree, COLLIDER finds the decision the specification forgot to make.”**
- signature second-act line:
  **“Tests say pass or fail. COLLIDER adds a third answer: nobody decided this yet.”**
- truth states: `OBSERVED`, `INFERRED`, `UNKNOWN`, `AGENT_DRIFT`, `SPEC_GAP`
- verdicts: `MERGE_ALLOWED`, `MERGE_BLOCKED`, `DECISION_REQUIRED`
- `KEEP UNKNOWN` is a valid product outcome
- comparative public fixture interpretations are PRESEEDED
- separate Bob evidence proves one real LIVE_BOB run
- fresh replay Attempt 01 = authentic `REPLAY_FAIL`
- fresh replay Attempt 02 = targeted-repair `REPLAY_PASS`
- controlled future guard probes are not autonomous agents

Never turn PRESEEDED public demo data into a fake LIVE_BOB claim.

## Why the current UI needs a final pass

The current UI is functional and coherent, but the visual language is still too
close to an editorial/scientific dashboard. It needs a stronger product-specific
identity that makes the **collision / judgment / decision-memory** mechanism
understandable before a judge reads labels.

The final UI should communicate, visually:

1. multiple agents can be locally green;
2. their assumptions can still collide;
3. the collision is not automatically an error;
4. COLLIDER distinguishes agent drift from a missing decision;
5. UNKNOWN must feel like a deliberate, authoritative stop state;
6. one human decision creates durable memory;
7. future changes are judged against that memory.

## Creative direction

Build a visual system around a **semantic collision chamber / decision instrument**.

The screen should feel like a purpose-built engineering instrument, not a generic
SaaS admin dashboard.

Core visual metaphor:

```text
API trajectory ─────╲
                     ╳  semantic collision
Ledger trajectory ──╱
                     │
                     ▼
              JUDGMENT / UNKNOWN
                     │
             human decision
                     │
             decision memory
                     │
              future guard
```

Use the name COLLIDER structurally. Agent lanes, vectors, convergence lines,
collision nodes, split paths, and canonical-memory traces should appear as real
information architecture, not decorative illustration.

## Visual character

Desired:

- ambitious, high-contrast, editorial-engineering visual language;
- light or mixed-light surface is fine, but **not a flat ivory page**;
- strong spatial composition and intentional asymmetry;
- sharp geometry and disciplined borders rather than generic card grids;
- one or two strong signal colors with semantic roles;
- readable typography with a distinct display/technical hierarchy;
- whitespace used for tension and hierarchy, not emptiness;
- information density appropriate for a serious developer tool;
- clear “instrument state” feeling.

Avoid:

- generic dark navy / black “AI product” aesthetic;
- neon-on-black hacker styling;
- purple/blue gradient blobs;
- glassmorphism;
- endless rounded cards/pills;
- stock dashboard grids;
- generic shadcn/Tailwind SaaS composition;
- fake terminal aesthetics;
- 3D decoration with no semantic job;
- animation added only because it looks impressive.

## Screen-specific goals

### 01 DETECT — local green, semantic collision

This should become the strongest opening frame.

Required visual contradiction:

- **30 local tests passed / 3 workstreams green**
- yet **2 integration conflicts**

Make the three workstreams visually distinct trajectories.
API and Ledger should visibly converge/collide around `customer_identity`.
Notifications should remain structurally separate for that concept.

The judge should understand “green locally ≠ agreed globally” without reading a
paragraph.

### 02 DECIDE — dramatic UNKNOWN / judgment state

This is the hero screen.

Make `SPEC_GAP / UNKNOWN` feel like an intentional safety state, not an error
toast.

The visual hierarchy should show:

```text
API      email
LEDGER   account_id
SOURCE   SILENT
---------------------
UNKNOWN
HUMAN DECISION REQUIRED
```

The source-silent condition is central.

`AGENT_DRIFT` and `SHARED_INFERRED` are secondary and must remain visually
distinguishable from the blocking SPEC_GAP.

The two decision paths remain:

- USE `account_id`
- KEEP UNKNOWN

KEEP UNKNOWN must look legitimate, not like a cancel button.

### 03–06 COMPILE / PATCH / VERIFY / REMEMBER

Show transformation, not a checklist dashboard.

The user should feel a decision being converted into durable system state:

```text
human answer
→ canon
→ targeted repair
→ verification
→ memory
```

Decision memory should feel like a durable protected artifact.

The transition from conflicts `2 → 0` should be visually obvious.

### 07 GUARD — judgment screen

This should feel like the final semantic court / CI gate.

The three verdicts must be immediately distinguishable:

- MERGE_BLOCKED
- MERGE_ALLOWED
- DECISION_REQUIRED

The signature future-change case must create a strong contrast:

**37/37 tests pass**  
but  
**DECISION_REQUIRED**

Do not make this look like a normal test-results page.

### PROOF / EVIDENCE

Evidence should be accessible without visually dominating Active Mode.

Use the proof drawer as an audit layer: receipts, hashes, provenance, diffs.

If Bob proof is surfaced in the UI, label it clearly as **observed evidence from a
separate LIVE_BOB run**. Never imply that the PRESEEDED public fixture was
generated live by Bob.

## Motion grammar

Rule: **motion must have a job**.

Use motion only for:

- orientation;
- causal sequence;
- collision/convergence;
- transition between epistemic states;
- human decision → durable memory;
- future change → semantic verdict;
- restoration after a guard probe.

Potential motion behaviors:

- agent trajectories enter independently and converge;
- collision node resolves into `SPEC_GAP / UNKNOWN`;
- decision commit causes a canonical trace to propagate to dependent workstreams;
- conflict count physically collapses `2 → 0`;
- future-change vector hits memory and produces verdict;
- proof drawer reveals evidence after verdict, not before.

Respect `prefers-reduced-motion`. Reduced motion must remain fully comprehensible.

## Reference-intelligence routing

Use these as principle sources, not templates to copy:

- Inspora — cross-disciplinary composition / identity / typography / motion ideas
- Zajno Motion — purposeful motion grammar and temporal hierarchy
- Rare UI / interaction libraries — mechanism references, not visual cloning
- Mobbin / product references — clarity and interaction patterns
- archival / print / scientific-instrument references when useful for distinctive
  information framing

Do not collapse the result into generic UI-library aesthetics.

## Technical constraints

Preserve:

- existing API/runtime contracts;
- existing semantic flow;
- existing element IDs and data attributes relied on by `app.js`, unless you
  update every dependent reference safely;
- ACTIVE/EVIDENCE mode behavior;
- proof drawer behavior;
- mobile behavior;
- accessibility semantics and keyboard usability;
- Cloudflare static asset deployment;
- no secrets in client code.

Do not change backend semantics.

Do not relabel evidence.

Do not alter test expectations just to fit the redesign.

## Implementation scope

Primary files:

- `demo-ui/index.html`
- `demo-ui/styles.css`
- `demo-ui/app.js` only when interaction/motion requires it

Touch `loop-state.js` or evidence data only if absolutely necessary and without
changing semantic truth.

## Quality gates

Before declaring complete:

1. Desktop judge view: 1440×900 or comparable
   - signature message readable above the fold
   - no scrolling required for the current active state
   - DETECT and DECIDE visually distinct in <5 seconds

2. Mobile: ~390×844
   - no horizontal overflow
   - primary decision action reachable
   - proof/evidence still usable

3. Reduced motion
   - `prefers-reduced-motion: reduce` produces a complete experience

4. Truth boundary
   - PRESEEDED and LIVE_BOB are never conflated
   - KEEP UNKNOWN remains valid
   - all three Semantic CI verdicts remain exact

5. Functional regression
   - existing app flow still works
   - proof drawer still works
   - ACTIVE/EVIDENCE modes still work
   - public runtime APIs unchanged

6. Verification
   - run repository tests
   - run TypeScript check
   - do not weaken tests to make the UI pass

## Deliverable standard

Do not stop at a design critique or moodboard.

Execute the redesign in code.

At completion provide:

- concise design rationale;
- files changed;
- functional changes, if any;
- desktop/mobile/reduced-motion validation summary;
- exact test/typecheck results;
- any residual UI risk;
- commit SHA / branch.

## Execution instruction for Claude Code

Read this file first, then inspect the current `demo-ui/` implementation and
relevant product truth docs.

Do not reopen product strategy.

Do not ask for aesthetic approval after every micro-step.

Make one coherent, ambitious UI/UX pass, validate it, and leave the repository in
a reviewable state.

Primary goal:

> **Make COLLIDER look like the only interface this product could have had.**
