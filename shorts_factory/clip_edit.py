#!/usr/bin/env python3
"""Commentary-style clip editor: cut dead air, add speaker-labelled subtitles,
*action* captions and spotlight zooms (the "news reel" format).

    python clip_edit.py edits/<name>.json

Edit file (times are in SOURCE seconds; they are remapped after the cuts):
{
  "source": "path/to/clip.mp4",
  "out": "path/to/output.mp4",
  "cuts": [[0.0, 2.4, 0.7], [4.0, 9.6]],       # segments to KEEP; optional 3rd value =\n                                                  # hold the frame at that time until then (skip blur)
  "credit": "Video: @original_filmer",          # optional small credit, top-left
  "speakers": {"Bystander": "#5AD15A", "Officer": "#E63C3C"},
  "lines": [                                     # subtitles
    {"t": [0.46, 1.86], "who": "Bystander", "text": "You guys do not have permission"},
    {"t": [0.0, 2.2], "who": "Officer", "text": "searches the teen's pockets", "action": true, "y": 980}
  ],
  "spotlights": [{"t": [12.55, 13.55], "x": 480, "y": 950, "zoom": 1.6, "r": 230}]
}
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920


def bgr(hex_rgb: str) -> str:
    h = hex_rgb.lstrip("#")
    return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


def ts(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


class Timeline:
    def __init__(self, cuts):
        self.cuts = [(c[0], c[1]) for c in cuts]
        self.offsets, acc = [], 0.0
        for a, b in self.cuts:
            self.offsets.append(acc)
            acc += b - a
        self.duration = acc

    def map_range(self, a: float, b: float):
        """Map a source interval to output intervals (it may span several cuts)."""
        out = []
        for (ca, cb), off in zip(self.cuts, self.offsets):
            lo, hi = max(a, ca), min(b, cb)
            if hi - lo > 0.05:
                out.append((off + lo - ca, off + hi - ca))
        return out


def spotlight_mask(path: str, cx: float, cy: float, r: float, darkness: int = 190):
    m = Image.new("L", (W, H), darkness)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(r * 0.18))
    rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rgba.putalpha(m)
    rgba.save(path)


def build(spec_path: str) -> str:
    spec = json.load(open(spec_path))
    base = os.path.dirname(os.path.abspath(spec_path))
    src = os.path.join(base, spec["source"]) if not os.path.isabs(spec["source"]) else spec["source"]
    out = os.path.join(base, spec["out"]) if not os.path.isabs(spec["out"]) else spec["out"]
    work = os.path.splitext(out)[0] + "_work"
    os.makedirs(work, exist_ok=True)
    tl = Timeline(spec["cuts"])
    spots = spec.get("spotlights", [])

    # ---- split cuts into pieces so spotlight sections can be zoomed ----------
    pieces = []  # (src_a, src_b, spotlight or None)
    for cut in spec["cuts"]:
        a, b = cut[0], cut[1]
        vfrom = cut[2] if len(cut) > 2 else a  # hold first clear frame until this time
        marks = sorted({a, b} | {x for s in spots for x in s["t"] if a < x < b})
        for p, q in zip(marks, marks[1:]):
            sp = next((s for s in spots if s["t"][0] <= p and q <= s["t"][1]), None)
            pieces.append((p, q, sp, vfrom if p == a else p))

    inputs = ["-i", src]
    fc, vlabels = [], []
    mask_idx = {}
    for i, (p, q, sp, vfrom) in enumerate(pieces):
        fade = 0.012
        fc.append(f"[0:a]atrim={p}:{q},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d={fade},afade=t=out:st={max(0, q - p - fade)}:d={fade}[a{i}]")
        v = f"[0:v]trim={vfrom}:{q},setpts=PTS-STARTPTS,scale={W}:{H},setsar=1"
        if vfrom > p:  # freeze the first clear frame so audio stays in sync
            v += f",tpad=start_duration={vfrom - p:.3f}:start_mode=clone"
        if sp:
            z = sp.get("zoom", 1.6)
            cw, ch = W / z, H / z
            x0 = min(max(0, sp["x"] - cw / 2), W - cw)
            y0 = min(max(0, sp["y"] - ch / 2), H - ch)
            # where the target lands after the zoom
            nx, ny = (sp["x"] - x0) * z, (sp["y"] - y0) * z
            mpath = os.path.join(work, f"mask{i}.png")  # one input per piece (ffmpeg can't reuse)
            spotlight_mask(mpath, nx, ny, sp.get("r", 230))
            inputs += ["-loop", "1", "-i", mpath]
            mask_idx[i] = len(mask_idx) + 1
            v += (f",crop={cw:.0f}:{ch:.0f}:{x0:.0f}:{y0:.0f},scale={W}:{H},setsar=1[vz{i}];"
                  f"[vz{i}][{mask_idx[i]}:v]overlay=shortest=1,setsar=1[v{i}]")
        else:
            v += f"[v{i}]"
        fc.append(v)
        vlabels.append(f"[v{i}][a{i}]")
    fc.append("".join(vlabels) + f"concat=n={len(pieces)}:v=1:a=1[vc][ac]")

    # ---- subtitles ------------------------------------------------------------
    speakers = spec.get("speakers", {})
    ass = os.path.join(work, "subs.ass")
    lines = [f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Medium,68,&H00FFFFFF,&H00FFFFFF,&H64000000,&H00000000,0,0,0,0,100,100,0,0,3,12,0,5,140,140,0,1
Style: Credit,Inter SemiBold,34,&H40FFFFFF,&H40FFFFFF,&H90000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,40,40,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""]
    events = []
    for ln in spec["lines"]:
        who = ln.get("who")
        color = bgr(speakers.get(who, "#FFFFFF")) if who else None
        y = ln.get("y", 1180)
        label = (r"{\fs46\b1\c" + color + "}" + who + r":\N" + r"{\r}") if who else ""
        txt = ln["text"].replace("{", "(").replace("}", ")")
        if ln.get("action"):
            body = r"{\i1\c&H00D7FF&}*" + txt + r"*{\r}"
        else:
            body = txt
        for a, b in tl.map_range(*ln["t"]):
            events.append((a, b + ln.get("hold", 0.12), y,
                           r"{\an5\pos(" + f"{W // 2},{y}" + r")}" + label + body))
    # same-position subtitles must not overlap
    events.sort()
    for i, e in enumerate(events):
        nxt = next((f for f in events[i + 1:] if f[2] == e[2]), None)
        end = min(e[1], nxt[0]) if nxt else min(e[1], tl.duration)
        lines.append(f"Dialogue: 0,{ts(e[0])},{ts(end)},Sub,,0,0,0,,{e[3]}")
    if spec.get("credit"):
        lines.append(f"Dialogue: 1,{ts(0)},{ts(tl.duration)},Credit,,0,0,0,,{spec['credit']}")
    open(ass, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    fc.append(f"[vc]ass={ass}[vout]")
    fc.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    cmd = (["ffmpeg", "-y", "-v", "error"] + inputs +
           ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
            "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])
    subprocess.run(cmd, check=True)
    print(f"[done] {out}  ({tl.duration:.1f}s from {len(spec['cuts'])} cuts)")
    return out


if __name__ == "__main__":
    build(sys.argv[1])
