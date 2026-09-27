# Runtime / Commit Binding Receipt — 2026-09-27

## Live Worker version

The real-iPhone production recording showed, under PROOF → PROVENANCE:

- Worker version UUID:
  `364ad4fd-7eb3-4918-aef8-f9ad049ee20a`

The same recording was against:

https://collider-semantic-ci.faadil-casecraft.workers.dev/

## Cloudflare deployment history

A subsequent Cloudflare dashboard recording showed Version History entry:

- Version short id: `364ad4fd`
- message: `docs: mark live session isolation proven`
- branch: `claude/sharp-planck-vfqz40`

The short id is the first 8 characters of the Worker version UUID observed in-product.

The Cloudflare build detail for that deployment showed:

- branch: `claude/sharp-planck-vfqz40`
- Git commit: `e185e84d`
- message: `docs: mark live session isolation proven`
- deploy command: `npx wrangler deploy`
- build succeeded

GitHub resolves that short commit to:

`e185e84d9d1cf00dfa1700b6bd2439e57887a291`

## Binding chain

`public PROVENANCE UUID 364ad4fd-7eb3-4918-aef8-f9ad049ee20a`
→ Cloudflare Version History `364ad4fd`
→ Cloudflare build `e185e84d`
→ GitHub commit `e185e84d9d1cf00dfa1700b6bd2439e57887a291`

## Verdict

**Runtime / Commit Binding: PROVEN**

This receipt binds the mobile/public runtime that produced the observed three-verdict product behavior to an exact Git commit.

Later deployments shown in Cloudflare are documentation/state descendants. This receipt does not claim that every later Cloudflare version has the same UUID; it proves the specific production runtime observed in the mobile recording.
