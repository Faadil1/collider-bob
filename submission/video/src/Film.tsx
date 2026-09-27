import React from "react";
import {
  AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, interpolate,
  staticFile, useCurrentFrame,
} from "remotion";
import events from "../public/events.json";
import { CHAPTERS, Callout, Cam, DURATION, FPS, H, LINES, Role, SHOTS, Shot, W } from "./timeline";

// ---------------------------------------------------------------------------
// Frame layout: a paper canvas holding the product window at native 1600x900.
// ---------------------------------------------------------------------------
const WIN_X = 160;
const WIN_Y = 70;

const C = {
  paper: "#e5e7df", plate: "#f1f2ec", ink: "#0c0d0a", muted: "#5f6259",
  ok: "#06845a", hit: "#e1162e", hold: "#d4f23a", api: "#2a36f5", ledger: "#ff6a13",
};
const ROLE: Record<Role, { stroke: string; chip: string; text: string }> = {
  ok: { stroke: C.ok, chip: C.ok, text: "#fff" },
  hit: { stroke: C.hit, chip: C.hit, text: "#fff" },
  hold: { stroke: C.ink, chip: C.hold, text: C.ink },
  ink: { stroke: C.ink, chip: C.ink, text: C.plate },
  api: { stroke: C.api, chip: C.api, text: "#fff" },
  ledger: { stroke: C.ledger, chip: C.ledger, text: "#fff" },
};

const ease = Easing.bezier(0.65, 0, 0.35, 1);
const out = Easing.bezier(0.16, 1, 0.3, 1);
const sec = (f: number) => f / FPS;

// ---------------------------------------------------------------------------
// Camera: zoom z centred on (x, y), clamped so the content always covers the
// window. Moves ease between keyframes; holds are true holds.
// ---------------------------------------------------------------------------
function camAt(cam: Cam[], t: number) {
  let a = cam[0], b = cam[cam.length - 1];
  for (let i = 0; i < cam.length - 1; i++) {
    if (t >= cam[i][0] && t <= cam[i + 1][0]) { a = cam[i]; b = cam[i + 1]; break; }
  }
  const p = b[0] === a[0] ? 1 : ease(Math.min(1, Math.max(0, (t - a[0]) / (b[0] - a[0]))));
  const z = a[1] + (b[1] - a[1]) * p;
  let x = a[2] + (b[2] - a[2]) * p;
  let y = a[3] + (b[3] - a[3]) * p;
  const hx = W / (2 * z), hy = H / (2 * z);
  x = Math.min(W - hx, Math.max(hx, x));
  y = Math.min(H - hy, Math.max(hy, y));
  return { z, x, y };
}

// window point -> screen point inside the window, for a camera state
const project = (c: { z: number; x: number; y: number }, px: number, py: number) =>
  [(px - c.x) * c.z + W / 2, (py - c.y) * c.z + H / 2];

// ---------------------------------------------------------------------------
// Cursor: replayed from the recorded mouse path (rec seconds).
// ---------------------------------------------------------------------------
type Ev = { t: number; name: string; from?: number[]; to?: number[]; at?: number[]; dur?: number };
const EV = events as Ev[];
const K = W / 1920;
function cursorAt(rec: number): { x: number; y: number; click: number } | null {
  const moves = EV.filter((e) => e.name.startsWith("move:"));
  if (!moves.length || rec < moves[0].t) return null;
  let pos = [moves[0].from![0], moves[0].from![1]];
  for (const m of moves) {
    if (rec < m.t) break;
    const p = Math.min(1, (rec - m.t) / 0.45);
    const e = ease(p);
    pos = [m.from![0] + (m.to![0] - m.from![0]) * e, m.from![1] + (m.to![1] - m.from![1]) * e];
  }
  const lastClick = EV.filter((e) => e.name.startsWith("click:") && e.t <= rec).pop();
  const since = lastClick ? rec - lastClick.t : 99;
  return { x: pos[0] * K, y: pos[1] * K, click: since };
}

const Cursor: React.FC<{ rec: number; cam: { z: number; x: number; y: number } }> = ({ rec, cam }) => {
  const c = cursorAt(rec);
  if (!c) return null;
  const [sx, sy] = project(cam, c.x, c.y);
  const ring = c.click < 0.5 ? c.click / 0.5 : null;
  return (
    <>
      {ring !== null && (
        <div style={{
          position: "absolute", left: sx - 28, top: sy - 28, width: 56, height: 56, borderRadius: 28,
          border: `3px solid ${C.ink}`, transform: `scale(${0.4 + ring * 0.9})`, opacity: 1 - ring,
        }} />
      )}
      <svg width={28} height={34} viewBox="0 0 28 34" style={{ position: "absolute", left: sx - 3, top: sy - 2 }}>
        <path d="M3 2 L3 26 L9.5 20 L14 31 L18.5 29 L14 18.5 L23 18.5 Z" fill={C.ink} stroke="#fff" strokeWidth={2} strokeLinejoin="round" />
      </svg>
    </>
  );
};

// ---------------------------------------------------------------------------
// Callout: an outline drawn around a real UI element, plus an exact label.
// ---------------------------------------------------------------------------
const CalloutView: React.FC<{ c: Callout; t: number; cam: { z: number; x: number; y: number } }> = ({ c, t, cam }) => {
  if (t < c.t || t > c.until) return null;
  const pad = c.pad ?? 6;
  const [x0, y0] = project(cam, c.r[0] - pad, c.r[1] - pad);
  const [x1, y1] = project(cam, c.r[0] + c.r[2] + pad, c.r[1] + c.r[3] + pad);
  const w = x1 - x0, h = y1 - y0;
  const inP = out(Math.min(1, (t - c.t) / 0.45));
  const outP = Math.min(1, (c.until - t) / 0.25);
  const perim = 2 * (w + h);
  const role = ROLE[c.role];
  const side = c.side ?? (y0 > 60 ? "above" : "below");
  const labelPos = side === "right"
    ? { left: x1 + 12, top: y0 + h / 2 - 20 }
    : { left: Math.max(8, Math.min(W - 620, x0)), top: side === "above" ? y0 - 46 : y1 + 8 };
  return (
    <div style={{ position: "absolute", left: 0, top: 0, opacity: outP }}>
      <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
        <rect x={x0} y={y0} width={w} height={h} fill="none" stroke={role.stroke} strokeWidth={4}
          strokeDasharray={perim} strokeDashoffset={perim * (1 - inP)} />
      </svg>
      {c.label && (
        <div style={{
          position: "absolute", ...labelPos,
          padding: "7px 12px", background: role.chip, color: role.text,
          font: "600 22px/1.2 'Plex Mono', monospace", whiteSpace: "nowrap",
          opacity: interpolate(t, [c.t + 0.15, c.t + 0.4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `translateY(${(1 - inP) * 8}px)`,
        }}>{c.label}</div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// One shot inside the window.
// ---------------------------------------------------------------------------
const ShotView: React.FC<{ s: Shot; prevSameState: boolean }> = ({ s, prevSameState }) => {
  const f = useCurrentFrame();
  const t = s.from + sec(f);
  const cam = camAt(s.cam, t);
  // Short dissolve between shots; the recording and its still are the same state.
  const fadeIn = prevSameState ? interpolate(f, [0, 6], [0, 1], { extrapolateRight: "clamp" }) : 1;
  const content = s.kind === "rec"
    ? <OffthreadVideo src={staticFile("product.mp4")} startFrom={Math.round(s.rec * FPS)} muted style={{ width: W, height: H }} />
    : <Img src={staticFile(`stills/${s.still}`)} style={{ width: W, height: H }} />;
  return (
    <AbsoluteFill style={{ opacity: fadeIn }}>
      <div style={{
        position: "absolute", width: W, height: H, transformOrigin: "0 0",
        transform: `translate(${W / 2 - cam.x * cam.z}px, ${H / 2 - cam.y * cam.z}px) scale(${cam.z})`,
      }}>{content}</div>
      {(s.callouts ?? []).map((c, i) => <CalloutView key={i} c={c} t={t} cam={cam} />)}
      {s.kind === "rec" && <Cursor rec={s.rec + sec(f)} cam={cam} />}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Chrome of the film: chapter band, captions, open and close.
// ---------------------------------------------------------------------------
const Mark: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <path d="M2 8 L20 20" stroke={C.api} strokeWidth={4} fill="none" />
    <path d="M2 32 L20 20" stroke={C.ledger} strokeWidth={4} fill="none" />
    <path d="M20 20 L38 20" stroke={C.ink} strokeWidth={3} fill="none" />
    <circle cx={20} cy={20} r={4.5} fill={C.hold} stroke={C.ink} strokeWidth={2.5} />
  </svg>
);

const ChapterBand: React.FC<{ t: number }> = ({ t }) => {
  const current = [...CHAPTERS].reverse().find(([s]) => t >= s);
  const names = CHAPTERS.slice(0, 5).map(([, n]) => n);
  return (
    <div style={{
      position: "absolute", left: WIN_X, top: 0, width: W, height: WIN_Y, display: "flex",
      alignItems: "center", gap: 28, font: "600 20px/1 Archivo, sans-serif", color: C.muted,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, color: C.ink }}>
        <Mark size={30} />
        <span style={{ font: "900 24px/1 Archivo", fontStretch: "125%" }}>COLLIDER</span>
      </div>
      <div style={{ display: "flex", gap: 22, marginLeft: 24 }}>
        {names.map((n) => {
          const on = current?.[1] === n;
          return (
            <span key={n} style={{
              color: on ? C.ink : C.muted, fontWeight: on ? 800 : 500,
              borderBottom: `3px solid ${on ? C.ink : "transparent"}`, paddingBottom: 4,
            }}>{n}</span>
          );
        })}
      </div>
      <span style={{ marginLeft: "auto", font: "500 17px/1 'Plex Mono', monospace" }}>recorded from the running product</span>
    </div>
  );
};

const Captions: React.FC<{ t: number }> = ({ t }) => {
  const line = LINES.find((l) => t >= l.start - 0.05 && t <= l.start + l.dur + 0.25);
  if (!line) return null;
  const o = interpolate(t, [line.start - 0.05, line.start + 0.12, line.start + line.dur + 0.1, line.start + line.dur + 0.25], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{
      position: "absolute", left: WIN_X, top: WIN_Y + H + 18, width: W, textAlign: "center",
      font: "500 30px/1.3 Archivo, sans-serif", color: C.ink, opacity: o,
    }}>{line.caption}</div>
  );
};

const Opening: React.FC<{ t: number }> = ({ t }) => {
  if (t > 2.2) return null;
  const o = interpolate(t, [0, 0.35, 1.6, 2.1], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: o, background: C.paper }}>
      <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
        <Mark size={96} />
        <span style={{ font: "900 120px/1 Archivo", fontStretch: "125%", letterSpacing: "-0.02em", color: C.ink }}>COLLIDER</span>
      </div>
      <div style={{ marginTop: 26, font: "500 36px/1.2 Archivo", color: C.muted }}>Semantic CI for AI agents</div>
    </AbsoluteFill>
  );
};

// Close: the live product steps aside, it is not covered.
const CLOSE_AT = 104.4;
const closeP = (t: number) => out(Math.min(1, Math.max(0, (t - CLOSE_AT) / 1.0)));

const EndCard: React.FC<{ t: number }> = ({ t }) => {
  if (t < CLOSE_AT + 0.3) return null;
  const p = out(Math.min(1, (t - CLOSE_AT - 0.3) / 0.8));
  return (
    <div style={{ position: "absolute", left: WIN_X, top: 300, width: 700, opacity: p, transform: `translateY(${(1 - p) * 16}px)` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <Mark size={64} />
        <span style={{ font: "900 84px/1 Archivo", fontStretch: "125%", letterSpacing: "-0.02em", color: C.ink }}>COLLIDER</span>
      </div>
      <div style={{ marginTop: 22, font: "700 38px/1.2 Archivo", color: C.ink }}>Semantic CI for AI agents</div>
      <div style={{ marginTop: 30, display: "flex", flexWrap: "wrap", gap: 10, font: "600 21px/1 'Plex Mono', monospace" }}>
        <span style={{ padding: "7px 10px", background: C.hit, color: "#fff" }}>MERGE_BLOCKED</span>
        <span style={{ padding: "7px 10px", background: C.ok, color: "#fff" }}>MERGE_ALLOWED</span>
        <span style={{ padding: "7px 10px", background: C.hold, color: C.ink }}>DECISION_REQUIRED</span>
      </div>
      <div style={{ marginTop: 40, font: "500 20px/1.6 'Plex Mono', monospace", color: C.muted }}>
        collider-semantic-ci.faadil-casecraft.workers.dev<br />github.com/Faadil1/collider-bob
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------

const fonts = `
@font-face { font-family: "Archivo"; src: url("${staticFile("fonts/archivo-wdth.woff2")}") format("woff2"); font-weight: 100 900; font-stretch: 62% 125%; }
@font-face { font-family: "Plex Mono"; src: url("${staticFile("fonts/plex-mono-500.woff2")}") format("woff2"); font-weight: 500; }
@font-face { font-family: "Plex Mono"; src: url("${staticFile("fonts/plex-mono-600.woff2")}") format("woff2"); font-weight: 600; }
@font-face { font-family: "Plex Mono"; src: url("${staticFile("fonts/plex-mono-700.woff2")}") format("woff2"); font-weight: 700; }
`;

export const Film: React.FC = () => {
  const f = useCurrentFrame();
  const t = sec(f);
  // the window opens with a left-to-right wipe after the title
  const wipe = interpolate(t, [1.8, 2.5], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  return (
    <AbsoluteFill style={{ background: C.paper }}>
      <style>{fonts}</style>
      <ChapterBand t={t} />
      <div style={{
        position: "absolute", left: WIN_X, top: WIN_Y, width: W, height: H, overflow: "hidden",
        background: C.plate, outline: `2px solid ${C.ink}`, clipPath: `inset(0 ${wipe}% 0 0)`,
        transformOrigin: "0 0",
        transform: `translate(${closeP(t) * (1920 - 120 - W * 0.56 - WIN_X)}px, ${closeP(t) * (300 - WIN_Y)}px) scale(${1 - 0.44 * closeP(t)})`,
      }}>
        {SHOTS.map((s, i) => (
          <Sequence key={i} from={Math.round(s.from * FPS)} durationInFrames={Math.round((s.to - s.from) * FPS)} layout="none">
            <ShotView s={s} prevSameState={i > 0} />
          </Sequence>
        ))}
      </div>
      <EndCard t={t} />
      <Captions t={t} />
      <Opening t={t} />
      {LINES.map((l, i) => (
        <Sequence key={i} from={Math.round(l.start * FPS)} durationInFrames={Math.ceil((l.dur + 0.2) * FPS)}>
          <Audio src={staticFile(l.file)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const TOTAL_FRAMES = Math.round(DURATION * FPS);
