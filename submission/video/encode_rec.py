"""Turn the screencast frames written by record.js into public/product.mp4.

CDP screencast frames arrive at irregular times; the concat demuxer gives each
frame its real duration, and ffmpeg resamples to a constant 30 fps. Stills and
the event log are copied next to it for the Remotion edit.
"""
import json
import os
import shutil
import subprocess
import sys

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
REC = os.environ.get("REC_OUT", os.path.join(HERE, "rec"))
PUB = os.path.join(HERE, "public")

frames = json.load(open(os.path.join(REC, "frames.json")))
lst = os.path.join(REC, "concat.txt")
with open(lst, "w") as f:
    for a, b in zip(frames, frames[1:] + [None]):
        f.write(f"file '{os.path.join(REC, a['file'])}'\n")
        f.write(f"duration {(b['t'] - a['t']) if b else 1 / 30:.4f}\n")
    f.write(f"file '{os.path.join(REC, frames[-1]['file'])}'\n")

subprocess.run([
    imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
    "-f", "concat", "-safe", "0", "-i", lst,
    "-vf", "fps=30,scale=1600:900:flags=lanczos,format=yuv420p",
    "-c:v", "libx264", "-crf", "14", "-preset", "slow",
    os.path.join(PUB, "product.mp4"),
], check=True)

shutil.copytree(os.path.join(REC, "stills"), os.path.join(PUB, "stills"), dirs_exist_ok=True)
shutil.copy(os.path.join(REC, "events.json"), os.path.join(PUB, "events.json"))
print("wrote public/product.mp4", file=sys.stderr)
