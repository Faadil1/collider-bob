# Final Runtime / Product-Tree Binding Receipt — 2026-09-27

## Purpose

This receipt closes the post-deployment paper gap without changing product code.

It distinguishes three things that must not be collapsed:

1. the **public Cloudflare Worker version** observed on the live origin;
2. the **product asset tree** that defines the polished COLLIDER UI;
3. later **documentation / evidence-packaging commits** on `main`.

## Public runtime observation

Public-origin verification recorded:

- URL: https://collider-semantic-ci.faadil-casecraft.workers.dev/
- Worker version: `453a881f-3b9a-4065-b65b-25b3b2ffa369`
- execution environment: `CLOUDFLARE_CONTAINER`
- public demo interpretation source: `PRESEEDED`
- human decision source: `INTERACTIVE_WEB`

This receipt does **not** relabel PRESEEDED browser interpretations as LIVE_BOB.

## Product-tree anchor

The polished UI was merged at:

`91795b67dc8dfeec51e485ec7cea8ada0bace60c`

The repository was then checked through evidence-packaging commit:

`8e336c8e344d712749b4a886fae349630afc7c4c`

GitHub comparison from `91795b6...` through `8e336c8...` shows only README/state/evidence additions or edits. No `demo-ui/` product asset changed.

The exact Git blob identities are the same at the product anchor and the checked documentation descendant:

| Product asset | Git blob SHA |
|---|---|
| `demo-ui/app.js` | `4fc6f8304f6cd2c1a91474321888f273acdc8b8b` |
| `demo-ui/index.html` | `35914a2bdd90cb0b801cd6023688845f365a8a59` |
| `demo-ui/styles.css` | `4a108e71ebb2ef9bac2490845bb2369ff075e953` |
| `demo-ui/loop-state.js` | `46d459157a8fdfbe5f7b1b112697795e88611739` |

## Binding statement

The live Worker version `453a881f-3b9a-4065-b65b-25b3b2ffa369` was observed serving the polished product surface whose `demo-ui/` asset set is anchored at `91795b67dc8dfeec51e485ec7cea8ada0bace60c`.

Later commits through `8e336c8e344d712749b4a886fae349630afc7c4c` do not change those product assets; they change documentation, state, and evidence packaging.

Therefore this receipt does **not** claim that the Worker was built from the later documentation-only HEAD. It proves product-asset equivalence and preserves the distinction between runtime provenance and repository packaging history.

## Historical receipt

`evidence/runtime/RUNTIME-COMMIT-BINDING-2026-09-27.md` remains preserved as the earlier mobile/runtime binding for Worker version `364ad4fd-7eb3-4918-aef8-f9ad049ee20a`.

## Verdict

**Runtime / Product-Tree Binding: PROVEN**

No product or pipeline change is authorized by this receipt.
