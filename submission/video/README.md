# COLLIDER judge film

**COLLIDER: Semantic CI for AI Agents** runs 1:51 at 1920x1080 and 30 fps. It uses H.264 video with AAC audio, loudness-normalised to -16 LUFS with a -1.5 dBTP ceiling.

| Deliverable | File |
|---|---|
| Master / judge version | `out/COLLIDER-semantic-ci-film.mp4` (not committed; rebuild below) |
| Voiceover script | `VOICEOVER-SCRIPT.md` (source of truth: `voiceover.json`) |
| Shot list | `SHOT-LIST.md` |
| Captions | `COLLIDER-semantic-ci-film.srt`, `COLLIDER-semantic-ci-film.vtt` (sidecar; captions are also burned in) |

## How it is made

1. **Footage** (`record.js`): Playwright drives the real product UI through DETECT, DECIDE, COMPILE, GUARD A/B/C, Proof and Evidence.
   - It records a CDP screencast at 1600x900.
   - It writes a mouse, click and element-rect event log.
   - It takes 3200x1800 stills at settled states.
2. **Encode** (`encode_rec.py`): converts the screencast frames to a constant 30 fps `public/product.mp4`.
3. **Voice** (`synth_voiceover.py`): Kokoro TTS (`kokoro-onnx`, voice `af_heart`) renders one WAV per sentence, so every caption carries its exact duration.
4. **Edit** (`src/`, Remotion 4):
   - `timeline.ts` holds every shot, camera keyframe, callout and VO start time.
   - `Film.tsx` renders the paper canvas, product window, camera, callouts, replayed cursor, captions, chapters and end card.

Callouts are anchored to rects logged during the recording. They are not hand-placed over imagined UI.

## Rebuild

```bash
# 1. product, from the repo root
python3 demo-ui/server.py &            # http://127.0.0.1:4173

# 2. footage
cd submission/video
npm ci
NODE_PATH=$(npm root -g) node record.js   # needs playwright-core; CHROME_PATH, COLLIDER_URL, REC_OUT optional
python3 encode_rec.py                     # needs imageio-ffmpeg

# 3. voice (needs kokoro-onnx plus kokoro-v1.0.onnx and voices-v1.0.bin)
python3 synth_voiceover.py

# 4. render
REMOTION_BROWSER=/path/to/chrome-headless-shell CONCURRENCY=3 OUT=out/collider-film-raw.mp4 node render.mjs
ffmpeg -i out/collider-film-raw.mp4 -c:v copy -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 48000 \
  -c:a aac -b:a 192k -movflags +faststart out/COLLIDER-semantic-ci-film.mp4
```

`STILLS=12.0,86.0 node render.mjs` renders single test frames into `out/`.

## Honesty notes

- The footage is the `design/claude-uiux-pass` build running **locally**, so the badge reads LOCAL ACTIVE DEMO. The public workers.dev deployment could not be reached from the build container because egress is blocked. It is the same UI and the same preseeded fixture. The end card gives the public URL.
- The demo's interpretations are PRESEEDED, and the film says so. LIVE_BOB is shown only as the separate evidence run, with attempt 01 FAIL 5/7 and attempt 02 targeted PASS 7/7.
- The HyperFrames library was not used. The "hyperframe" treatment (punch-ins, framing, camera moves, stroke callouts) is built in Remotion.
- Remotion is free for individuals and companies of up to 3 people. Larger organisations need a company licence (see remotion.dev/license). Kokoro-82M is Apache-2.0. The fonts (Archivo, IBM Plex Mono) are OFL and ship with `demo-ui/fonts/`.
