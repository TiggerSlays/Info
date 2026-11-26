#!/usr/bin/env python3
"""Script JSON  ->  finished 1080x1920 YouTube Short (voice, captions, music, SFX).

    python make_short.py scripts/illusions_01.json [--out ../output]

Pipeline (mirrors the workflow taught in the source video, with original footage):
  1. Script: hook (0-3s) -> curiosity build (3-10s) -> payoff (10-45s) -> CTA
  2. Voiceover: neural TTS per segment, silences trimmed for pace
  3. Captions: Whisper word timestamps -> bold, one-word-highlighted captions
  4. Visuals: code-rendered scenes + punch-in zooms + red circle/arrow callouts
  5. Sound: whoosh on cuts, pop on callouts, music bed ducked to -22 dB
  6. Export: H.264/AAC MP4, plus thumbnail and upload metadata
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio  # noqa: E402
import captions  # noqa: E402
import scenes  # noqa: E402

FPS = 30
GAP = 0.14  # seconds of breath between segments


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def build(script_path: str, out_dir: str) -> str:
    spec = json.load(open(script_path))
    slug = spec["slug"]
    work = os.path.join(out_dir, slug + "_work")
    os.makedirs(work, exist_ok=True)
    voice_name = spec.get("voice", "am_michael")
    speed = spec.get("speed", 1.12)
    t0 = time.time()

    # ---- 1-2. voiceover --------------------------------------------------
    segs = spec["segments"]
    pieces, cursor = [], 0.0
    words, seg_bounds = [], []
    for s in segs:
        clip = audio.tts(s["text"], voice=voice_name, speed=speed)
        s["start"] = cursor
        s["end"] = cursor + len(clip) / audio.SR
        # "hold": keep the segment on screen at least this long (e.g. staring illusions)
        pad = max(GAP, s.get("hold", 0) - len(clip) / audio.SR)
        pieces += [clip, np.zeros(int(pad * audio.SR), dtype=np.float32)]
        cursor = s["end"] + pad
        w = s["text"].split()
        seg_bounds.append((s["start"], s["end"], len(words), len(words) + len(w)))
        s["word_range"] = (len(words), len(words) + len(w))
        words += w
    voice = np.concatenate(pieces)
    voice_path = os.path.join(work, "voice.wav")
    sf.write(voice_path, voice, audio.SR)
    print(f"[voice] {len(voice)/audio.SR:.1f}s  ({time.time()-t0:.0f}s)")

    # ---- 3. captions -----------------------------------------------------
    timed = captions.word_times(voice_path, words, seg_bounds)
    ass_path = os.path.join(work, "captions.ass")
    captions.build_ass(timed, ass_path, y=spec.get("caption_y", 1460))
    print(f"[captions] {len(timed)} words  ({time.time()-t0:.0f}s)")

    # resolve callouts given as "at_word" into seconds from segment start
    sfx = []
    prev_scene = None
    for s in segs:
        if s["scene"] != prev_scene or s.get("punch", True):
            sfx.append((max(0.0, s["start"] - 0.12), audio.whoosh()))
        prev_scene = s["scene"]
        i0, i1 = s["word_range"]
        for c in s.get("callouts", []):
            if "at_word" in c:
                target = _norm(c["at_word"])
                hits = [i for i in range(i0, i1) if _norm(words[i]) == target]
                n = c.get("occurrence", 0)
                if hits:
                    c["at"] = max(0.0, timed[hits[min(n, len(hits) - 1)]][1] - s["start"])
            c.setdefault("at", 0.0)
            sfx.append((s["start"] + c["at"], audio.pop()))

    # ---- 5. sound --------------------------------------------------------
    mixed = audio.mix(voice, sfx, music_db=spec.get("music_db", -22))
    audio_path = os.path.join(work, "mix.wav")
    sf.write(audio_path, mixed, audio.SR)
    total = len(mixed) / audio.SR

    # ---- 4. visuals + 6. export -----------------------------------------
    scene_start = {}
    run_start = None
    for i, s in enumerate(segs):
        if i == 0 or segs[i - 1]["scene"] != s["scene"]:
            run_start = s["start"]
        scene_start[i] = run_start

    out_mp4 = os.path.join(out_dir, slug + ".mp4")
    vf = f"ass={ass_path}"
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{scenes.W}x{scenes.H}", "-r", str(FPS), "-i", "-",
           "-i", audio_path, "-vf", vf,
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",  # YouTube plays back at ~-14 LUFS
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n_frames = int(total * FPS)
    seg_i = 0
    thumb_frame = None
    for f in range(n_frames):
        T = f / FPS
        while seg_i + 1 < len(segs) and T >= segs[seg_i + 1]["start"] - 0.02:
            seg_i += 1
        s = segs[seg_i]
        nxt = segs[seg_i + 1]["start"] if seg_i + 1 < len(segs) else total
        d = max(0.01, nxt - s["start"])
        lt = max(0.0, T - s["start"])
        ctx = {"t": T - scene_start[seg_i], "lt": lt, "d": d, "p": min(1.0, lt / d),
               "params": s.get("params", {})}
        img = scenes.SCENES[s["scene"]](ctx)
        scenes.draw_callouts(img, s.get("callouts"), lt)

        # punch-in: alternate base zoom on each cut + slow push-in (Ken Burns)
        z0 = 1.0 if seg_i % 2 == 0 else 1.07
        if not s.get("punch", True):
            z0 = 1.0
        z = z0 + s.get("push", 0.04) * ctx["p"]
        if z > 1.001:
            fx, fy = s.get("focus", (scenes.W / 2, scenes.H / 2))
            cw, ch = scenes.W / z, scenes.H / z
            x0 = min(max(0, fx - cw / 2), scenes.W - cw)
            y0 = min(max(0, fy - ch / 2), scenes.H - ch)
            img = img.resize((scenes.W, scenes.H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        if f == int(spec.get("thumb_at", 1.0) * FPS):
            thumb_frame = img.copy()
        proc.stdin.write(img.tobytes())
        if f % (FPS * 5) == 0:
            print(f"[render] {T:5.1f}/{total:.1f}s", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"[done] {out_mp4}  ({time.time()-t0:.0f}s)")

    # ---- thumbnail + metadata -------------------------------------------
    if thumb_frame is not None:
        th = thumb_frame
        d = ImageDraw.Draw(th)
        for k, line in enumerate(spec.get("thumb_text", [])):
            scenes.label(d, (scenes.W // 2, 1560 + k * 150), line, size=128,
                         fill=scenes.YELLOW if k == 0 else (255, 255, 255))
        th.save(os.path.join(out_dir, slug + "_thumb.jpg"), quality=92)
    meta = {k: spec[k] for k in ("title", "description", "tags") if k in spec}
    meta["duration_s"] = round(total, 2)
    meta["script"] = " ".join(s["text"] for s in segs)
    json.dump(meta, open(os.path.join(out_dir, slug + "_upload.json"), "w"), indent=2)
    return out_mp4


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    build(a.script, os.path.abspath(a.out))
