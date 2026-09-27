# COLLIDER: voiceover script

Voice: Kokoro TTS, `af_heart`, speed 1.0, synthesized per sentence (`synth_voiceover.py`).
Timings are output-video seconds. Where the caption differs from the spoken line, the caption carries the exact identifier (e.g. spoken "decision required", captioned `DECISION_REQUIRED`).

Spoken words: 235. Film length: 1:51.


## Hook

- **  2.0s** Three workstreams built one feature from one sentence.
- **  5.1s** Thirty tests pass. All three are green.
- **  7.8s** Integration still finds two conflicts.

## Problem

- ** 10.6s** Each workstream was locally right.
- ** 12.8s** API keys the customer by email. Ledger uses account_id. Notifications never touches it.
- ** 20.0s** COLLIDER checks each collision against the source.
- ** 22.8s** Where the brief already decided, it is agent drift. Where the brief is silent, it is a spec gap.  
  caption: Where the brief already decided: AGENT_DRIFT. Where the brief is silent: SPEC_GAP.

## Decide

- ** 29.0s** The brief names refund_amount, so Ledger is repaired from source.
- ** 33.0s** It never names a customer identity. So COLLIDER stops at UNKNOWN, and asks one question.
- ** 39.1s** Keeping UNKNOWN is a valid answer. Here, we choose account_id.

## Compile

- ** 43.7s** That answer compiles.
- ** 45.3s** The spec is patched, API and Ledger are repaired, a regression contract is written, and the decision is stored as memory.
- ** 53.2s** Two conflicts become zero.

## Guard A

- ** 57.0s** Now a future change puts email back. Tests fail, and decision memory blocks the merge.  
  caption: A future change puts email back. Tests fail, and decision memory blocks the merge: MERGE_BLOCKED.

## Guard B

- ** 66.3s** A wording change to the customer notice touches no decision. Merge allowed.  
  caption: A wording change to the customer notice touches no decision: MERGE_ALLOWED.

## Guard C

- ** 72.0s** Then Ledger switches to dollars. All thirty seven tests pass.  
  caption: Then Ledger switches to dollars. All 37 tests pass.
- ** 76.0s** COLLIDER still returns decision required, because nobody ever decided the money unit.  
  caption: COLLIDER still returns DECISION_REQUIRED, because nobody ever decided the money unit.

## Proof

- ** 84.3s** The demo data is preseeded, and labelled that way.
- ** 87.5s** Separately, IBM Bob ran the protocol live, with three independent agents.
- ** 92.7s** The first replay passed five of seven checks, and we kept that failure. A targeted replay passed seven of seven.

## Close

- **100.3s** COLLIDER is semantic CI for AI agents.
- **103.5s** When agents disagree, it finds the decision the specification forgot to make.
