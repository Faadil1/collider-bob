// The whole edit, in output seconds. Every shot is either a segment of the
// real product recording (rec seconds) or a high-resolution still captured
// from the same run at a settled state. Nothing on screen is mocked.

import events from "../public/events.json";
import vo from "../public/vo/manifest.json";
import voCfg from "../voiceover.json";

export const FPS = 30;
export const W = 1600; // product window, native recording size
export const H = 900;

// Recording rects are logged in 1920x1080 space; the window is 1600x900.
const K = 1600 / 1920;
type Rect = [number, number, number, number];
export const rect = (event: string, key: string): Rect => {
  const e = (events as any[]).find((x) => x.name === event);
  const r = e?.rects?.[key];
  if (!r) throw new Error(`missing rect ${event}.${key}`);
  return r.map((v: number) => v * K) as Rect;
};
export const center = (r: Rect): [number, number] => [r[0] + r[2] / 2, r[1] + r[3] / 2];

// Camera keyframe: at output second t, zoom z centred on window point (x, y).
export type Cam = [t: number, z: number, x: number, y: number];
export type Role = "ok" | "hit" | "hold" | "ink" | "api" | "ledger";
export type Callout = { t: number; until: number; r: Rect; label?: string; role: Role; pad?: number; side?: "above" | "below" | "right" };

export type Shot =
  | { kind: "rec"; from: number; to: number; rec: number; cam: Cam[]; callouts?: Callout[] }
  | { kind: "still"; from: number; to: number; still: string; cam: Cam[]; callouts?: Callout[] };

const FULL = (t: number): Cam => [t, 1, W / 2, H / 2];
const at = (t: number, z: number, r: Rect, dx = 0, dy = 0): Cam => {
  const [x, y] = center(r);
  return [t, z, x + dx, y + dy];
};

// ---- narration placement ------------------------------------------------
export type Line = { file: string; start: number; dur: number; caption: string };
const byScene = (id: string) => (vo as any[]).filter((v) => v.scene === id);
const captionsFor = (id: string): string[] =>
  (voCfg as any).scenes.find((s: any) => s.id === id).captions;
const place = (id: string, starts: number[]): Line[] =>
  byScene(id).map((v: any, i: number) => ({
    file: v.file, dur: v.dur, start: starts[i], caption: captionsFor(id)[i],
  }));

export const LINES: Line[] = [
  ...place("hook", [2.0, 5.1, 7.8]),
  ...place("problem", [10.6, 12.75, 20.0, 22.8]),
  ...place("decide", [29.0, 32.95, 39.1]),
  ...place("compile", [43.7, 45.3, 53.2]),
  ...place("guardA", [57.0]),
  ...place("guardB", [66.3]),
  ...place("guardC", [72.0, 76.0]),
  ...place("bob", [84.3, 87.55, 92.7]),
  ...place("close", [100.3, 103.5]),
];

// ---- rects used by the camera and callouts --------------------------------
const D = "detect:settled", DC = "decide:settled", C = "compile:settled";
const R = {
  tests: rect(D, "tests"), suites: rect(D, "suites"), conflicts: rect(D, "conflicts"),
  ledgerCol: rect(D, "ledger"), chamber: rect(D, "chamber"), hitA: rect(D, "hitA"),
  hitB: rect(D, "hitB"), notif: rect(D, "notif"), status: rect(D, "status"),
  api: rect(DC, "api"), ledgerR: rect(DC, "ledgerR"), source: rect(DC, "source"),
  plate: rect(DC, "plate"), word: rect(DC, "word"), drift: rect(DC, "drift"),
  assume: rect(DC, "assume"), decision: rect(DC, "decision"), commit: rect(DC, "commit"),
  keep: rect(DC, "keep"), readings: rect(DC, "readings"),
  spine: rect(C, "spine"), checklist: rect(C, "checklist"), collapse: rect(C, "collapse"),
  number: rect(C, "number"), memory: rect(C, "memory"), lanes: rect(C, "lanes"), result: rect(C, "result"),
  docket: rect("guardA:p2", "docket"), bench: rect("guardA:p2", "bench"),
  conv: rect("guardA:p2", "conv"), sem: rect("guardA:p2", "sem"), cf: rect("guardA:p2", "cf"),
  replay: rect("replay:rail", "replay"), bob: rect("proof:bobsection", "bob"),
};
// Truth badge in the top bar (not logged; measured from the captured still).
const BADGE: Rect = [1040, 10, 350, 40];

// Recording offsets (rec seconds) for the footage shots.
export const SHOTS: Shot[] = [
  // HOOK: the DETECT entrance, then the contradiction.
  { kind: "rec", from: 1.8, to: 4.4, rec: 0.2, cam: [FULL(1.8), FULL(4.4)] },
  { kind: "still", from: 4.4, to: 10.5, still: "detect-settled.png",
    cam: [FULL(4.4), FULL(4.9), at(5.6, 1.7, R.ledgerCol, 0, -70), at(7.5, 1.7, R.ledgerCol, 0, -70), at(8.3, 1.28, R.ledgerCol, 330, 40), at(10.5, 1.3, R.ledgerCol, 330, 40)],
    callouts: [
      { t: 5.3, until: 7.7, r: R.tests, label: "30 tests pass", role: "ok" },
      { t: 6.2, until: 7.7, r: R.suites, label: "3/3 green", role: "ok", side: "right" },
      { t: 8.2, until: 10.5, r: R.conflicts, label: "2 integration conflicts", role: "hit" },
    ] },

  // PROBLEM: where the workstreams collide, then COLLIDER classifies.
  { kind: "still", from: 10.5, to: 20.0, still: "detect-settled.png",
    cam: [at(10.5, 1.3, R.ledgerCol, 330, 40), at(12.4, 1.75, R.hitA, 10, 10), at(16.6, 1.75, R.hitA, 10, 10), at(17.8, 1.55, R.notif, 40, -40), at(20.0, 1.5, R.notif, 40, -40)],
    callouts: [
      { t: 12.9, until: 17.0, r: R.hitA, label: "customer_identity: email vs account_id", role: "hit", pad: 8 },
      { t: 17.9, until: 20.0, r: R.notif, label: "Notifications: no customer_identity claim", role: "ink", pad: 12 },
    ] },
  { kind: "rec", from: 20.0, to: 22.5, rec: 6.45, cam: [FULL(20.0), FULL(22.5)] },
  { kind: "still", from: 22.5, to: 28.9, still: "decide-settled.png",
    cam: [FULL(22.5), at(23.4, 1.45, R.drift, 120, -40), at(25.4, 1.45, R.drift, 120, -40), at(26.2, 1.45, R.plate, 0, -60), at(28.9, 1.45, R.plate, 0, -60)],
    callouts: [
      { t: 23.4, until: 25.8, r: R.drift, label: "AGENT_DRIFT: the brief decided", role: "hit", pad: 6 },
      { t: 26.3, until: 28.9, r: R.plate, label: "SPEC_GAP: the brief is silent", role: "hold", pad: 6 },
    ] },

  // DECIDE: authority ends; one human answer.
  { kind: "still", from: 28.9, to: 38.9, still: "decide-settled.png",
    cam: [at(28.9, 1.45, R.plate, 0, -60), at(29.8, 1.9, R.drift, 60, 0), at(32.6, 1.9, R.drift, 60, 0), at(33.6, 1.8, R.source, -40, 0), at(35.4, 1.8, R.source, -40, 0), at(36.4, 1.35, R.plate, 0, -30), at(38.9, 1.45, R.plate, 0, -30)],
    callouts: [
      { t: 30.0, until: 32.5, r: R.drift, label: "refund_amount: repaired from source", role: "hit", pad: 6 },
      { t: 33.7, until: 35.4, r: R.source, role: "ink", pad: 4 },
    ] },
  { kind: "rec", from: 38.9, to: 47.0, rec: 12.3,
    cam: [at(38.9, 1.3, R.decision, -60, 30), at(42.6, 1.3, R.decision, -60, 30), FULL(43.6), FULL(47.0)],
    callouts: [
      { t: 39.4, until: 41.3, r: R.keep, label: "KEEP UNKNOWN: a valid abstention", role: "hold", pad: 6, side: "below" },
      { t: 41.5, until: 42.6, r: R.commit, label: "Use account_id", role: "ink", pad: 6 },
    ] },

  // COMPILE: the decision becomes durable state.
  { kind: "still", from: 47.0, to: 55.6, still: "compile-settled.png",
    cam: [FULL(47.0), at(47.8, 1.55, R.spine, 60, -230), at(51.9, 1.55, R.spine, 60, 150), at(53.0, 1.45, R.result, 0, -110), at(55.6, 1.5, R.result, 0, -110)],
    callouts: [
      { t: 53.3, until: 55.6, r: R.collapse, label: "2 → 0", role: "ok", pad: 4 },
    ] },

  // GUARD: three future changes, judged live.
  { kind: "rec", from: 55.6, to: 62.7, rec: 22.8, cam: [FULL(55.6), FULL(58.6), at(59.8, 1.15, R.bench, 0, 0), at(62.7, 1.15, R.bench, 0, 0)] },
  { kind: "still", from: 62.7, to: 63.9, still: "guardA-p4.png", cam: [at(62.7, 1.15, R.bench, 0, 0), at(63.9, 1.35, R.cf, 0, -80)],
    callouts: [{ t: 62.8, until: 63.9, r: R.cf, role: "ink", pad: 4 }] },
  { kind: "rec", from: 63.9, to: 71.5, rec: 31.8, cam: [FULL(63.9), FULL(67.6), at(68.6, 1.15, R.bench), at(71.5, 1.15, R.bench)] },
  { kind: "rec", from: 71.5, to: 78.7, rec: 41.2, cam: [FULL(71.5), FULL(74.4), at(75.4, 1.2, R.bench, 0, -40), at(78.7, 1.2, R.bench, 0, -40)] },
  { kind: "still", from: 78.7, to: 84.0, still: "guardC-p4.png",
    // The product already labels both sides; the camera only pushes in.
    cam: [at(78.7, 1.2, R.bench, 0, -40), at(80.0, 1.42, R.bench, 0, -70), at(81.6, 1.42, R.bench, 0, -70), at(82.4, 1.6, R.docket, 0, 40), at(84.0, 1.6, R.docket, 0, 40)] },

  // PROOF: provenance, the separate LIVE_BOB run, and replay evidence.
  { kind: "still", from: 84.0, to: 87.4, still: "guardC-p4.png",
    cam: [at(84.0, 1.6, R.docket, 0, 40), at(84.9, 2.0, BADGE, 0, 60), at(87.4, 2.0, BADGE, 0, 60)],
    callouts: [{ t: 85.0, until: 87.4, r: BADGE, label: "PRESEEDED, and labelled", role: "ink", pad: 6 }] },
  { kind: "rec", from: 87.4, to: 91.1, rec: 51.6, cam: [FULL(87.4), FULL(91.1)] },
  { kind: "still", from: 91.1, to: 96.2, still: "proof-provenance.png",
    cam: [FULL(91.1), at(92.0, 1.55, R.bob, 0, 0), at(96.2, 1.6, R.bob, 0, 20)],
    callouts: [{ t: 92.2, until: 96.2, r: R.bob, label: "Separate LIVE_BOB run", role: "ink", pad: 6 }] },
  { kind: "still", from: 96.2, to: 99.8, still: "replay-rail.png",
    cam: [at(96.2, 1.6, R.replay, 300, -150), at(97.2, 2.4, R.replay, 60, -20), at(99.8, 2.4, R.replay, 60, -20)],
    callouts: [{ t: 97.3, until: 99.8, r: R.replay, role: "ink", pad: 8 }] },

  // CLOSE: back to the live product.
  { kind: "rec", from: 99.8, to: 104.0, rec: 67.3, cam: [FULL(99.8), FULL(104.0)] },
  { kind: "still", from: 104.0, to: 111.0, still: "guardC-p4.png", cam: [FULL(104.0), FULL(111.0)] },
];

export const DURATION = 111.0;

// Chapters shown in the top band (output seconds).
export const CHAPTERS: [number, string][] = [
  [1.8, "Detect"], [20.9, "Decide"], [42.3, "Compile"], [55.6, "Guard"], [84.0, "Proof"], [104.0, "COLLIDER"],
];
