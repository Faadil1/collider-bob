// Renders the COLLIDER film. Uses a local headless Chromium when
// REMOTION_BROWSER is set (the sandbox cannot download one).
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";

const browserExecutable = process.env.REMOTION_BROWSER || null;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "Collider", browserExecutable });

const stills = (process.env.STILLS || "").split(",").filter(Boolean);
if (stills.length) {
  for (const s of stills) {
    const frame = Math.round(Number(s) * composition.fps);
    await renderStill({ serveUrl, composition, frame, output: `out/frame-${s}.png`, browserExecutable });
    console.log("still", s);
  }
  process.exit(0);
}

const outputLocation = process.env.OUT || "out/collider-film.mp4";
await renderMedia({
  serveUrl, composition, codec: "h264", crf: 14, x264Preset: "slow", audioBitrate: "192k",
  // near-lossless frame capture and standard-range BT.709 output, so UI text stays crisp
  jpegQuality: 98, pixelFormat: "yuv420p", colorSpace: "bt709",
  outputLocation, browserExecutable, concurrency: Number(process.env.CONCURRENCY || 4),
  onProgress: ({ progress }) => { if (Math.round(progress * 100) % 10 === 0) process.stdout.write(`\r${Math.round(progress * 100)}%`); },
});
console.log("\nwrote", outputLocation);
