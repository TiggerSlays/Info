#!/usr/bin/env python3
"""Pull public vidIQ channel stats pages (markdown versions) and summarise them.

Usage: python vidiq_scan.py channels.json out.json
channels.json: {"niche name": ["@handle" or "UC...channelId", ...], ...}

For each channel this reports what the tutorial's niche checklist asks for:
views in the last 28 days, subscriber growth, upload frequency, country,
and how its recent Shorts perform (median views, best outlier).
"""
from __future__ import annotations

import json
import re
import statistics
import sys
import time
import urllib.request

BASE = "https://vidiq.com/youtube-stats/channel/{}/index.md"
UA = {"User-Agent": "Mozilla/5.0 (research script)"}


def fetch(ch: str) -> str | None:
    try:
        req = urllib.request.Request(BASE.format(ch), headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        print(f"  ! {ch}: {e}", file=sys.stderr)
        return None


def num(s: str) -> float:
    return float(s.replace(",", ""))


def parse(md: str) -> dict:
    out: dict = {}
    m = re.search(r"^# (.+?) YouTube Stats", md, re.M)
    out["name"] = m.group(1) if m else "?"
    m = re.search(r"channel-evidence: (\{.*?\}) -->", md)
    if m:
        ev = json.loads(m.group(1))
        out.update(subs=ev.get("subscribers"), total_views=ev.get("views"),
                   videos=ev.get("videos"), est_rev=ev.get("estimatedAdRevenueUsd"),
                   as_of=ev.get("observationDate"))
    m = re.search(r"Over the last 28 days, it ([^.]*)\.", md)
    s28 = m.group(1) if m else ""
    g = re.search(r"(gained|lost) ([\d,]+) subscribers", s28)
    out["subs_28d"] = (-1 if g and g.group(1) == "lost" else 1) * num(g.group(2)) if g else 0
    v = re.search(r"averaged ([\d,]+) views per day", s28)
    out["views_per_day"] = num(v.group(1)) if v else None
    u = re.search(r"published ([\d,]+) videos?", s28)
    out["uploads_28d"] = int(num(u.group(1))) if u else 0
    for key, pat in (("country", r"- Country: ([^(\n]+)"), ("category", r"- Category: ([^(\n]+)"),
                     ("joined", r"- Joined YouTube: ([\d-]+)")):
        m = re.search(pat, md)
        out[key] = m.group(1).strip() if m else None

    def table(title):
        sec = re.search(rf"## {title}\n\n(.*?)(?:\n## |\Z)", md, re.S)
        rows = []
        if not sec:
            return rows
        for line in sec.group(1).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6 and re.match(r"\d{4}-\d\d-\d\d", cells[2] or ""):
                title_txt = re.sub(r"^\[|\]\(.*$", "", cells[0]).replace("\n", " ")
                try:
                    views = num(cells[3])
                except ValueError:
                    continue
                rows.append({"title": title_txt[:70], "format": cells[1], "date": cells[2],
                             "views": views, "outlier": cells[5]})
        return rows

    out["top"] = table("Top videos")
    out["latest"] = table("Latest videos")
    shorts = [r["views"] for r in out["latest"] if r["format"] == "Short"]
    out["latest_shorts_n"] = len(shorts)
    out["latest_shorts_median"] = statistics.median(shorts) if shorts else None
    out["latest_shorts_max"] = max(shorts) if shorts else None
    return out


if __name__ == "__main__":
    chans = json.load(open(sys.argv[1]))
    results = {}
    for niche, lst in chans.items():
        results[niche] = []
        for ch in lst:
            md = fetch(ch)
            time.sleep(1.0)  # be polite
            if not md:
                continue
            row = parse(md)
            row["id"] = ch
            results[niche].append(row)
            vpd = row.get("views_per_day")
            print(f"{niche[:12]:12} {row['name'][:28]:28} subs={row.get('subs')} "
                  f"v/day={vpd} up28={row.get('uploads_28d')} medShort={row.get('latest_shorts_median')}")
    json.dump(results, open(sys.argv[2], "w"), indent=1)
