"""Voiceover (Kokoro neural TTS), procedural music bed and sound effects.

Everything here is generated locally:
  * Voice: Kokoro-82M (Apache-2.0), an open model that rivals paid TTS.
  * Music: synthesised lo-fi loop, so there are no Content ID claims.
  * SFX: whoosh on cuts, pop on callouts, like the source video's SFX layer.
"""
from __future__ import annotations

import os
from functools import lru_cache

import numpy as np

SR = 24000
MODELS = os.environ.get("KOKORO_DIR", os.path.expanduser("/home/user/models"))


@lru_cache(maxsize=1)
def _kokoro():
    from kokoro_onnx import Kokoro
    return Kokoro(os.path.join(MODELS, "kokoro-v1.0.int8.onnx"),
                  os.path.join(MODELS, "voices-v1.0.bin"))


def tts(text: str, voice: str = "am_michael", speed: float = 1.12) -> np.ndarray:
    samples, sr = _kokoro().create(text, voice=voice, speed=speed, lang="en-us")
    assert sr == SR, sr
    samples = np.asarray(samples, dtype=np.float32)
    # trim leading/trailing silence so cuts stay tight (retention!)
    thr = 0.01
    nz = np.where(np.abs(samples) > thr)[0]
    if len(nz):
        samples = samples[max(0, nz[0] - int(0.03 * SR)): nz[-1] + int(0.06 * SR)]
    return samples


# --------------------------------------------------------------------------- #
# Music bed: 92 BPM lo-fi loop (pad chords + soft kick/hat), fully synthesised.
# --------------------------------------------------------------------------- #
def _env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e.astype(np.float32)


def music_bed(seconds: float, bpm: float = 92, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    out = np.zeros(n, dtype=np.float32)
    beat = 60 / bpm
    # i - vi - IV - V style progression (Am F C G) as frequencies
    chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6],
              [196.0, 261.6, 329.6], [196.0, 246.9, 293.7]]
    bar = beat * 4
    t_all = np.arange(n) / SR
    for i in range(int(seconds / bar) + 1):
        s = int(i * bar * SR)
        e = min(n, int((i + 1) * bar * SR))
        if s >= n:
            break
        tt = t_all[s:e] - t_all[s]
        seg = np.zeros(e - s, dtype=np.float32)
        for f in chords[i % 4]:
            seg += 0.10 * np.sin(2 * np.pi * f * tt) + 0.03 * np.sin(2 * np.pi * 2 * f * tt)
        fade = np.minimum(1, tt / 0.25) * np.minimum(1, (bar - tt) / 0.25)
        out[s:e] += seg * fade.astype(np.float32)
    # drums
    kick_n = int(0.25 * SR)
    kt = np.arange(kick_n) / SR
    kick = (np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 25)) * kt) * _env(kick_n, 0.002, 0.08))
    hat_n = int(0.05 * SR)
    hat = rng.standard_normal(hat_n).astype(np.float32) * _env(hat_n, 0.001, 0.01) * 0.15
    k = 0
    while k * beat < seconds:
        s = int(k * beat * SR)
        if k % 2 == 0:
            out[s:s + kick_n] += 0.5 * kick[: max(0, min(kick_n, n - s))]
        hs = int((k + 0.5) * beat * SR)
        if hs < n:
            out[hs:hs + hat_n] += hat[: max(0, min(hat_n, n - hs))]
        k += 1
    out += rng.standard_normal(n).astype(np.float32) * 0.004  # vinyl hiss
    return out / (np.max(np.abs(out)) + 1e-9)


def whoosh() -> np.ndarray:
    n = int(0.35 * SR)
    rng = np.random.default_rng(1)
    noise = rng.standard_normal(n).astype(np.float32)
    # crude sweeping low-pass via moving average of decreasing width
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 2
    smooth = np.convolve(noise, np.ones(8) / 8, mode="same")
    return (smooth * env * 0.5).astype(np.float32)


def pop() -> np.ndarray:
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 300
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.04) * 0.6).astype(np.float32)


def db(x: float) -> float:
    return 10 ** (x / 20)


def mix(voice: np.ndarray, sfx_events: list[tuple[float, np.ndarray]],
        music_db: float = -22.0) -> np.ndarray:
    """Voice on top, music bed ducked underneath (the video used -20 dB)."""
    n = len(voice) + int(0.6 * SR)
    out = np.zeros(n, dtype=np.float32)
    out[: len(voice)] += voice
    bed = music_bed(n / SR)[:n] * db(music_db)
    out += bed
    for t, clip in sfx_events:
        s = int(t * SR)
        e = min(n, s + len(clip))
        if s < n:
            out[s:e] += clip[: e - s] * db(-8)
    peak = np.max(np.abs(out)) + 1e-9
    return (out / peak * db(-1.0)).astype(np.float32)
