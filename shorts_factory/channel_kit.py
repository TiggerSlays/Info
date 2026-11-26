#!/usr/bin/env python3
"""Channel branding: 800x800 profile picture + 2560x1440 banner (YouTube specs).

The source video generated these with an AI image tool; here they are drawn
in code from the channel's own visual motif (the café-wall illusion), so the
brand matches the content and is fully owned.

    python channel_kit.py --name "BRAIN GLITCH" --tagline "One illusion a day"
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import RED, YELLOW, _font  # noqa: E402


def cafe_pattern(w, h, tile, mortar=4, dark=(0, 0, 0), light=(255, 255, 255)):
    img = Image.new("RGB", (w, h), light)
    d = ImageDraw.Draw(img)
    shifts = [0, 1 / 3, 2 / 3, 1 / 3]
    for r in range(h // tile + 1):
        y0 = r * tile
        x = -tile * 2 + int(shifts[r % 4] * tile)
        while x < w:
            d.rectangle([x, y0, x + tile - 1, y0 + tile], fill=dark)
            x += tile * 2
        d.rectangle([0, y0 - mortar // 2, w, y0 + mortar // 2], fill=(110, 110, 110))
    return img


def glitch_text(img, center, text, size):
    """RGB-split 'glitch' wordmark: red/cyan offsets under a yellow fill."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = _font(size)
    cx, cy = center
    off = max(4, size // 22)
    d.text((cx - off, cy), text, font=f, fill=(255, 30, 60, 230), anchor="mm")
    d.text((cx + off, cy), text, font=f, fill=(0, 220, 255, 230), anchor="mm")
    d.text((cx, cy), text, font=f, fill=YELLOW + (255,), anchor="mm",
           stroke_width=max(3, size // 30), stroke_fill=(0, 0, 0, 255))
    img.paste(layer, (0, 0), layer)


def profile_picture(name: str, out: str):
    S = 800
    bg = cafe_pattern(S, S, 100)
    bg = Image.blend(bg, Image.new("RGB", (S, S), (14, 14, 18)), 0.78)
    d = ImageDraw.Draw(bg)
    d.ellipse([60, 60, S - 60, S - 60], outline=RED, width=26)
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    glitch_text(bg, (S // 2, S // 2 + 10), initials, 330)
    bg.save(out, quality=95)


def banner(name: str, tagline: str, out: str):
    Wb, Hb = 2560, 1440
    img = cafe_pattern(Wb, Hb, 120)
    # vignette toward the safe area (1546x423, centred) so text always reads
    yy, xx = np.mgrid[0:Hb, 0:Wb]
    dist = np.sqrt(((xx - Wb / 2) / (Wb / 2)) ** 2 + ((yy - Hb / 2) / (Hb / 3)) ** 2)
    a = np.clip(1.15 - dist, 0, 1)[..., None] * 0.9
    arr = np.asarray(img).astype(np.float32)
    arr = arr * (1 - a) + np.array([14, 14, 18]) * a
    arr = arr * 0.55 + np.array([14, 14, 18]) * 0.45
    img = Image.fromarray(arr.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    glitch_text(img, (Wb // 2, Hb // 2 - 40), name, 190)
    d = ImageDraw.Draw(img)
    d.text((Wb // 2, Hb // 2 + 110), tagline.upper(), font=_font(64), fill=(255, 255, 255),
           anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
    img.save(out, quality=95)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="BRAIN GLITCH")
    ap.add_argument("--tagline", default="One illusion a day. Your brain will hate it.")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "channel"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    profile_picture(a.name, os.path.join(a.out, "profile_800x800.jpg"))
    banner(a.name, a.tagline, os.path.join(a.out, "banner_2560x1440.jpg"))
    print("wrote", a.out)
