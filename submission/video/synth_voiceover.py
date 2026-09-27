# Synthesize the COLLIDER voiceover one sentence at a time.
# Captions keep exact identifiers; the voice gets a speakable variant.
import json, os, re, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
V = "/home/user/collider-bob/submission/video"
SPOKEN = [(r"refund_amount", "refund amount"), (r"account_id", "account I D"), (r"\bIBM\b", "I B M")]
def speakable(s):
    for a, b in SPOKEN: s = re.sub(a, b, s)
    return s
cfg = json.load(open(f"{V}/voiceover.json"))
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
os.makedirs(f"{V}/public/vo", exist_ok=True)
out = []
for sc in cfg["scenes"]:
    for i, line in enumerate(sc["lines"]):
        s, sr = k.create(speakable(line), voice=cfg["voice"], speed=cfg["speed"], lang="en-us")
        a = np.abs(s); idx = np.where(a > 0.01)[0]
        s = s[max(0, idx[0] - int(.03 * sr)): idx[-1] + int(.08 * sr)]
        f = f"vo/{sc['id']}-{i}.wav"; sf.write(f"{V}/public/{f}", s, sr)
        out.append({"scene": sc["id"], "i": i, "file": f, "dur": round(len(s) / sr, 3), "text": line})
json.dump(out, open(f"{V}/public/vo/manifest.json", "w"), indent=1)
print(round(sum(o["dur"] for o in out), 1), "s of speech in", len(out), "lines")
