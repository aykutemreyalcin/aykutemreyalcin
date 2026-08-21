#!/usr/bin/env python3
"""Ping the sites I run, keep a rolling history, and redraw the status board.

Deliberately stdlib-only so the workflow needs no install step.
"""

from __future__ import annotations

import json
import pathlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
HISTORY_FILE = ROOT / "data" / "uptime.json"
SVG_FILE = ROOT / "assets" / "status.svg"

SITES = [
    ("aykutemreyalcin.com", "https://aykutemreyalcin.com", "personal site"),
    ("fosapps.com", "https://fosapps.com", "shopify utilities"),
    ("enretag.com", "https://enretag.com", "fulfillment platform"),
]

# 28 checks at one every 6 hours is a rolling week.
WINDOW = 28
TIMEOUT = 20
USER_AGENT = "Mozilla/5.0 (compatible; profile-uptime-bot/1.0; +https://github.com/aykutemreyalcin)"


def probe(url: str) -> dict:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            code = response.status
            response.read(2048)
    except urllib.error.HTTPError as exc:
        code = exc.code
    except Exception:
        code = 0

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return {"up": 0 < code < 400, "code": code, "ms": elapsed_ms}


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"sites": {}}


def status_text(entry: dict) -> str:
    if entry["code"] == 0:
        return "unreachable / timed out"
    if entry["up"]:
        return "up &#183; http %d" % entry["code"]
    return "down &#183; http %d" % entry["code"]


def bar_strip(history: list, x0: int, y: int) -> str:
    """Draw the rolling window right-aligned so the newest check sits last."""
    parts = []
    padding = WINDOW - len(history)
    for index in range(WINDOW):
        x = x0 + index * 10
        if index < padding:
            parts.append('<rect class="slot" x="%d" y="%d" width="7" height="14" rx="2"/>' % (x, y))
            continue
        entry = history[index - padding]
        css = "ok" if entry["up"] else "bad"
        parts.append('<rect class="%s" x="%d" y="%d" width="7" height="14" rx="2"/>' % (css, x, y))
    return "\n  ".join(parts)


def render(history: dict, now: datetime) -> str:
    rows = []
    for offset, (name, _url, label) in enumerate(SITES):
        row_y = 80 + offset * 44
        entries = history["sites"].get(name, [])
        latest = entries[-1] if entries else {"up": False, "code": 0, "ms": 0}
        uptime = (sum(1 for e in entries if e["up"]) / len(entries) * 100) if entries else 0.0
        dot = "ok" if latest["up"] else "bad"
        latency = "%d ms" % latest["ms"] if latest["up"] else "--"

        rows.append(
            """
  <circle class="{dot}dot" cx="36" cy="{dot_y}" r="5"/>
  <text class="mono name fg"   x="52" y="{row_y}">{name}</text>
  <text class="mono sub muted" x="52" y="{sub_y}">{label} &#183; {status}</text>
  {bars}
  <text class="mono tiny muted" x="770" y="{row_y}" text-anchor="end">{uptime:.1f}%</text>
  <text class="mono tiny muted" x="850" y="{row_y}" text-anchor="end">{latency}</text>""".format(
                dot=dot,
                dot_y=row_y - 4,
                row_y=row_y,
                sub_y=row_y + 13,
                name=name,
                label=label,
                status=status_text(latest),
                bars=bar_strip(entries, 430, row_y - 11),
                uptime=uptime,
                latency=latency,
            )
        )

    return TEMPLATE.format(
        rows="\n".join(rows),
        stamp=now.strftime("%Y-%m-%d %H:%M UTC"),
    )


TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="880" height="215" viewBox="0 0 880 215" role="img" aria-label="Live status of the sites I run">
  <title>Live systems</title>
  <style>
    svg {{
      --bg: #ffffff;
      --card: #f6f8fa;
      --line: #d0d7de;
      --fg: #1f2328;
      --muted: #6e7781;
      --green: #2da44e;
      --red: #cf222e;
      --track: #e6eaef;
    }}
    @media (prefers-color-scheme: dark) {{
      svg {{
        --bg: #0d1117;
        --card: #161b22;
        --line: #30363d;
        --fg: #e6edf3;
        --muted: #8b949e;
        --green: #3fb950;
        --red: #f85149;
        --track: #21262d;
      }}
    }}
    .bg     {{ fill: var(--bg); }}
    .stroke {{ stroke: var(--line); fill: none; }}
    .fg     {{ fill: var(--fg); }}
    .muted  {{ fill: var(--muted); }}
    .slot   {{ fill: var(--track); }}
    .ok     {{ fill: var(--green); }}
    .bad    {{ fill: var(--red); }}
    .mono   {{ font-family: ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }}
    .name   {{ font-size: 12.5px; font-weight: 600; }}
    .sub    {{ font-size: 8.5px; letter-spacing: 0.05em; }}
    .tiny   {{ font-size: 9px; letter-spacing: 0.08em; }}
    .okdot  {{ fill: var(--green); animation: beat 2.4s ease-in-out infinite; }}
    .baddot {{ fill: var(--red); animation: beat 1s ease-in-out infinite; }}
    @keyframes beat {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.35; }} }}
  </style>

  <rect class="bg" x="0" y="0" width="880" height="215" rx="16"/>
  <rect class="stroke" x="0.5" y="0.5" width="879" height="214" rx="16"/>

  <text class="mono tiny muted" x="30" y="34">LIVE SYSTEMS</text>
  <text class="mono tiny muted" x="850" y="34" text-anchor="end">SELF HOSTED CHECK &#183; EVERY 6H</text>

  <text class="mono tiny muted" x="430" y="58">LAST 7 DAYS</text>
  <text class="mono tiny muted" x="770" y="58" text-anchor="end">UPTIME</text>
  <text class="mono tiny muted" x="850" y="58" text-anchor="end">LATENCY</text>
{rows}

  <text class="mono sub muted" x="30" y="205">last checked {stamp}</text>
</svg>
"""


def main() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    history = load_history()
    history.setdefault("sites", {})

    for name, url, _label in SITES:
        entry = probe(url)
        entry["ts"] = now.isoformat().replace("+00:00", "Z")
        series = history["sites"].setdefault(name, [])
        series.append(entry)
        del series[:-WINDOW]
        print("%-24s %s http=%s %sms" % (name, "up  " if entry["up"] else "DOWN", entry["code"], entry["ms"]))

    history["updated"] = now.isoformat().replace("+00:00", "Z")

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2) + "\n")

    SVG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SVG_FILE.write_text(render(history, now))


if __name__ == "__main__":
    main()
