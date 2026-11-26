"""Original visual generators for faceless Shorts (1080x1920).

Every visual is drawn from scratch in code, so the channel owns 100% of the
footage: no reused clips, no copyright claims, no "reused content" demonetization.

A scene function has the signature:
    scene(ctx) -> PIL.Image (RGB, W x H)
where ctx is a dict with:
    t        seconds since this scene started (continuous across segments)
    lt       seconds since the current segment started
    d        duration of the current segment
    p        lt / d  (0..1 progress through the segment)
    params   the segment's "params" dict from the script
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
BG = (14, 14, 18)
RED = (255, 40, 40)
YELLOW = (255, 214, 0)
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in (FONT_BLACK, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ramp(p: float, start: float, end: float) -> float:
    """0 before start, 1 after end, smooth in between."""
    if end <= start:
        return 1.0 if p >= start else 0.0
    return ease((p - start) / (end - start))


def label(draw: ImageDraw.ImageDraw, xy, text, size=110, fill=(255, 255, 255)):
    f = _font(size)
    draw.text(xy, text, font=f, fill=fill, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))


# --------------------------------------------------------------------------- #
# 1. Café wall illusion: perfectly straight lines that look tilted.
# --------------------------------------------------------------------------- #
CW_TOP, CW_ROWS, CW_TILE, CW_MORTAR = 250, 13, 80, 4


@lru_cache(maxsize=1)
def _cafe_wall_base() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    shifts = [0, 1 / 3, 2 / 3, 1 / 3]  # sawtooth third-tile shift: strongest tilt
    for r in range(CW_ROWS):
        y0 = CW_TOP + r * CW_TILE
        d.rectangle([0, y0, W, y0 + CW_TILE], fill=(255, 255, 255))
        off = int(shifts[r % 4] * CW_TILE)
        x = -CW_TILE * 2 + off
        while x < W:
            d.rectangle([x, y0, x + CW_TILE - 1, y0 + CW_TILE], fill=(0, 0, 0))
            x += CW_TILE * 2
    for r in range(CW_ROWS + 1):  # grey mortar lines
        y = CW_TOP + r * CW_TILE
        d.rectangle([0, y - CW_MORTAR // 2, W, y + CW_MORTAR // 2], fill=(110, 110, 110))
    return img


def cafe_wall(ctx) -> Image.Image:
    img = _cafe_wall_base().copy()
    prm = ctx["params"]
    draw = ImageDraw.Draw(img)
    rulers = prm.get("rulers", 0)  # 0 none, 1 animate in, 2 fully drawn
    if rulers:
        prog = 1.0 if rulers == 2 else ramp(ctx["p"], 0.15, 0.75)
        for r in range(1, CW_ROWS):
            y = CW_TOP + r * CW_TILE
            draw.line([(0, y), (int(W * prog), y)], fill=RED, width=6)
    if prm.get("dim_tiles"):
        a = ramp(ctx["p"], 0.0, 0.6) * 0.55
        overlay = Image.new("RGB", (W, H), BG)
        img = Image.blend(img, overlay, a)
        draw = ImageDraw.Draw(img)
        for r in range(1, CW_ROWS):
            y = CW_TOP + r * CW_TILE
            draw.line([(0, y), (W, y)], fill=RED, width=6)
    return img


# --------------------------------------------------------------------------- #
# 2. Stepping feet illusion: two blocks moving in sync appear to take turns.
# --------------------------------------------------------------------------- #
SF_STRIPE = 34
SF_SPEED = 150  # px / s
SF_BW, SF_BH = 220, 70


def stepping_feet(ctx) -> Image.Image:
    prm = ctx["params"]
    stripes = prm.get("stripes", 1.0)
    if isinstance(stripes, list):  # [from, to] fade across the segment
        stripes = stripes[0] + (stripes[1] - stripes[0]) * ramp(ctx["p"], 0.1, 0.6)

    arr = np.empty((H, W, 3), dtype=np.uint8)
    arr[:] = BG
    top, bot = 520, 1400
    xs = np.arange(W)
    stripe_row = np.where((xs // SF_STRIPE) % 2 == 0, 0, 255).astype(np.float32)
    grey = 128.0
    row = grey + (stripe_row - grey) * stripes
    arr[top:bot, :, :] = row[None, :, None].astype(np.uint8)
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)

    span = W + SF_BW
    x = (ctx["t"] * SF_SPEED) % span - SF_BW
    y1, y2 = 790, 1060
    d.rectangle([x, y1, x + SF_BW, y1 + SF_BH], fill=(255, 236, 60))   # light block
    d.rectangle([x, y2, x + SF_BW, y2 + SF_BH], fill=(20, 30, 120))    # dark block
    if prm.get("sync_line"):
        a = ramp(ctx["p"], 0.0, 0.3)
        if a > 0:
            d.line([(x, y1 - 40), (x, y2 + SF_BH + 40)], fill=RED, width=8)
            d.line([(x + SF_BW, y1 - 40), (x + SF_BW, y2 + SF_BH + 40)], fill=RED, width=8)
    return img


# --------------------------------------------------------------------------- #
# 3. Simultaneous contrast: two identical greys look different on a gradient.
# --------------------------------------------------------------------------- #
SC_GREY = 128
SC_SQ = 230
SC_A = (270, 960)
SC_B = (810, 960)


def same_color(ctx) -> Image.Image:
    prm = ctx["params"]
    flatten = 0.0
    if prm.get("bridge"):
        flatten = ramp(ctx["p"], 0.35, 0.85) if prm.get("flatten") else 0.0
    xs = np.linspace(0, 1, W, dtype=np.float32)
    grad = 15 + 225 * xs  # dark on the left, light on the right
    grad = grad + (SC_GREY * 0.0 + 70 - grad) * flatten  # flatten toward dark grey
    arr = np.empty((H, W, 3), dtype=np.uint8)
    arr[:] = grad[None, :, None].astype(np.uint8)
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    s = SC_SQ // 2
    for cx, cy in (SC_A, SC_B):
        d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(SC_GREY,) * 3)
    if prm.get("bridge"):
        prog = ramp(ctx["p"], 0.0, 0.35)
        x0, x1 = SC_A[0] + s, SC_B[0] - s
        d.rectangle([x0, SC_A[1] - 45, x0 + (x1 - x0) * prog, SC_A[1] + 45], fill=(SC_GREY,) * 3)
    if prm.get("labels", True):
        label(d, (SC_A[0], SC_A[1] - s - 90), "A")
        label(d, (SC_B[0], SC_B[1] - s - 90), "B")
    return img


# --------------------------------------------------------------------------- #
# 5. Lilac chaser: stare at the cross -> a green dot appears, pink dots vanish.
# --------------------------------------------------------------------------- #
LC_C = (540, 860)
LC_R, LC_N, LC_STEP = 330, 12, 0.125  # radius, dots, seconds per dot


@lru_cache(maxsize=LC_N)
def _lilac_frame(missing: int) -> Image.Image:
    img = Image.new("RGB", (W, H), (190, 190, 190))
    dots = Image.new("RGB", (W, H), (190, 190, 190))
    d = ImageDraw.Draw(dots)
    for k in range(LC_N):
        if k == missing:
            continue
        a = 2 * math.pi * k / LC_N - math.pi / 2
        x, y = LC_C[0] + LC_R * math.cos(a), LC_C[1] + LC_R * math.sin(a)
        d.ellipse([x - 52, y - 52, x + 52, y + 52], fill=(225, 120, 225))
    img = dots.filter(ImageFilter.GaussianBlur(22))
    d = ImageDraw.Draw(img)
    cx, cy = LC_C
    d.rectangle([cx - 28, cy - 5, cx + 28, cy + 5], fill=(0, 0, 0))
    d.rectangle([cx - 5, cy - 28, cx + 5, cy + 28], fill=(0, 0, 0))
    return img


def lilac_chaser(ctx) -> Image.Image:
    return _lilac_frame(int(ctx["t"] / LC_STEP) % LC_N).copy()


# --------------------------------------------------------------------------- #
# 6. Negative afterimage: stare at an inverted picture, then a greyscale one
#    looks full colour for a few seconds.
# --------------------------------------------------------------------------- #
AI_BOX = (90, 330, 990, 1230)  # 900x900 picture area


@lru_cache(maxsize=1)
def _landscape() -> Image.Image:
    w = h = 900
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    sky = np.stack([40 + 60 * y, 120 + 80 * y, 230 + 0 * y], -1) * np.ones((1, w, 1))
    img = Image.fromarray(sky.astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.ellipse([600, 90, 780, 270], fill=(255, 215, 0))                      # sun
    d.ellipse([-300, 520, 700, 1300], fill=(40, 170, 60))                   # hills
    d.ellipse([300, 580, 1300, 1400], fill=(20, 140, 45))
    d.rectangle([170, 470, 390, 640], fill=(210, 30, 30))                    # red house
    d.polygon([(150, 480), (280, 370), (410, 480)], fill=(120, 60, 20))
    d.rectangle([255, 560, 305, 640], fill=(255, 230, 120))
    for fx in range(480, 860, 70):                                          # flowers
        d.ellipse([fx, 760, fx + 34, 794], fill=(255, 70, 160))
    return img


def afterimage(ctx) -> Image.Image:
    prm = ctx["params"]
    img = Image.new("RGB", (W, H), (128, 128, 128))
    pic = _landscape()
    if prm.get("mode", "negative") == "negative":
        pic = Image.eval(pic, lambda v: 255 - v)
    else:
        pic = pic.convert("L").convert("RGB")
    img.paste(pic, AI_BOX[:2])
    d = ImageDraw.Draw(img)
    cx, cy = (AI_BOX[0] + AI_BOX[2]) // 2, (AI_BOX[1] + AI_BOX[3]) // 2
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=RED, outline=(0, 0, 0), width=3)
    if prm.get("countdown"):
        n = math.ceil(max(0.0, ctx["d"] - ctx["lt"]))
        if n > 0:
            label(d, (W // 2, 200), str(n), size=150, fill=YELLOW)
    return img


# --------------------------------------------------------------------------- #
# 4. End card: animated subscribe prompt using the channel brand colours.
# --------------------------------------------------------------------------- #
def end_card(ctx) -> Image.Image:
    prm = ctx["params"]
    img = _cafe_wall_base().copy()
    img = Image.blend(img, Image.new("RGB", (W, H), BG), 0.82)
    d = ImageDraw.Draw(img)
    name = prm.get("channel", "BRAIN GLITCH")
    pop = 1 + 0.06 * math.sin(ctx["t"] * 6)
    label(d, (W // 2, 760), name, size=int(118 * pop), fill=YELLOW)
    bw, bh = 640, 150
    a = ramp(ctx["p"], 0.15, 0.4)
    if a > 0:
        y = 1000
        d.rounded_rectangle([W // 2 - bw // 2, y, W // 2 + bw // 2, y + bh], radius=40,
                            fill=(int(255 * a), int(20 * a), int(20 * a)))
        label(d, (W // 2, y + bh // 2), "SUBSCRIBE", size=84)
    return img


SCENES = {
    "cafe_wall": cafe_wall,
    "stepping_feet": stepping_feet,
    "same_color": same_color,
    "end_card": end_card,
    "lilac_chaser": lilac_chaser,
    "afterimage": afterimage,
}


# --------------------------------------------------------------------------- #
# Callouts: red circles and arrows (the editing trick from the source video).
# --------------------------------------------------------------------------- #
def draw_callouts(img: Image.Image, callouts: list, lt: float) -> None:
    d = ImageDraw.Draw(img)
    for c in callouts or []:
        at = c.get("at", 0.0)
        if lt < at or lt > c.get("until", 1e9):
            continue
        k = ease((lt - at) / 0.18)  # quick pop-in
        if c["type"] == "circle":
            r = c["r"] * (0.6 + 0.4 * k)
            x, y = c["x"], c["y"]
            d.ellipse([x - r, y - r, x + r, y + r], outline=RED, width=14)
        elif c["type"] == "arrow":
            x0, y0, x1, y1 = c["from"] + c["to"]
            xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
            d.line([(x0, y0), (xe, ye)], fill=RED, width=18)
            ang = math.atan2(ye - y0, xe - x0)
            hl = 60
            pts = [(xe, ye),
                   (xe - hl * math.cos(ang - 0.5), ye - hl * math.sin(ang - 0.5)),
                   (xe - hl * math.cos(ang + 0.5), ye - hl * math.sin(ang + 0.5))]
            d.polygon(pts, fill=RED)
