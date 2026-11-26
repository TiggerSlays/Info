"""Word-by-word "viral" captions (CapCut-style) rendered as an ASS subtitle file.

Timing comes from Whisper word timestamps on the generated voiceover, aligned
back to the script's exact words so spelling is always correct.
"""
from __future__ import annotations

import difflib
import re

PLAY_W, PLAY_H = 1080, 1920


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def word_times(wav_path: str, script_words: list[str], seg_bounds: list[tuple[float, float, int, int]]):
    """Return [(word, start, end)] for every script word.

    seg_bounds: (start_s, end_s, first_word_idx, last_word_idx_exclusive) per segment,
    used as a fallback when Whisper misses words.
    """
    import whisper

    model = whisper.load_model("base.en")
    res = model.transcribe(wav_path, word_timestamps=True, language="en", fp16=False)
    hyp = [(w["word"].strip(), w["start"], w["end"])
           for s in res["segments"] for w in s.get("words", [])]

    a = [_norm(w) for w in script_words]
    b = [_norm(w) for w, _, _ in hyp]
    times: list[tuple[float, float] | None] = [None] * len(script_words)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            _, s, e = hyp[blk.b + k]
            times[blk.a + k] = (s, e)

    # Fill gaps by interpolating inside each segment's known boundaries.
    for s0, s1, i0, i1 in seg_bounds:
        idx = list(range(i0, i1))
        for j, i in enumerate(idx):
            if times[i] is not None and not (s0 - 0.3 <= times[i][0] <= s1 + 0.3):
                times[i] = None  # mis-match landed in another segment
        known = [(i, times[i]) for i in idx if times[i] is not None]
        anchors = [(i0 - 1, (s0, s0))] + known + [(i1, (s1, s1))]
        for (ia, ta), (ib, tb) in zip(anchors, anchors[1:]):
            gap = ib - ia - 1
            if gap <= 0:
                continue
            start, end = ta[1], tb[0]
            step = max(0.05, (end - start) / gap)
            for g in range(gap):
                times[ia + 1 + g] = (start + g * step, start + (g + 1) * step)
    return [(w, t[0], t[1]) for w, t in zip(script_words, times)]


def _ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(words: list[tuple[str, float, float]], out_path: str,
              max_words: int = 3, y: int = 1430, highlight: str = "&H0000D6FF&") -> None:
    """Groups of up to `max_words`; the word being spoken is yellow and pops."""
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {PLAY_W}
PlayResY: {PLAY_H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        ends_sentence = w[0].endswith((".", "?", "!", ","))
        if len(cur) >= max_words or ends_sentence:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    events = []
    for g in groups:
        g_end = words[g[-1]][2]
        for k, i in enumerate(g):
            start = words[i][1]
            end = words[g[k + 1]][1] if k + 1 < len(g) else g_end + 0.08
            parts = []
            for j in g:
                txt = words[j][0].upper().replace("{", "").replace("}", "")
                if j == i:
                    parts.append(r"{\c" + highlight + r"\fscx112\fscy112}" + txt + r"{\r}")
                else:
                    parts.append(txt)
            pop = r"{\pos(%d,%d)\t(0,70,\fscx104\fscy104)\t(70,140,\fscx100\fscy100)}" % (PLAY_W // 2, y)
            events.append([start, end, pop + " ".join(parts)])
    # Never show two caption events at once (they'd draw on top of each other).
    events.sort(key=lambda e: e[0])
    for a, b in zip(events, events[1:]):
        a[1] = min(a[1], b[0])
    lines = [f"Dialogue: 0,{_ts(s)},{_ts(e)},Cap,,0,0,0,,{txt}"
             for s, e, txt in events if e - s >= 0.01]
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(header + "\n".join(lines) + "\n")
