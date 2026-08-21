#!/usr/bin/env python3
"""Draw my own GitHub stats card.

The popular hosted cards (github-readme-stats, streak-stats) sit behind shared rate limits and
serve 503s or twenty second responses often enough to show up as a broken image. This pulls the
same numbers straight from the API and renders them in the same visual language as the rest of
the profile.
"""

from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.request
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
SVG_FILE = ROOT / "assets" / "stats.svg"

USER = os.environ.get("GITHUB_ACTOR", "aykutemreyalcin")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Linguist colours for the languages that actually show up in my repos.
LANG_COLORS = {
    "Java": "#b07219",
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Swift": "#F05138",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "C": "#555555",
    "Shell": "#89e051",
    "Kotlin": "#A97BFF",
    "Dockerfile": "#384d54",
    "Makefile": "#427819",
}
FALLBACK_COLOR = "#8b949e"
TOP_LANGS = 6


def api(path: str) -> object:
    request = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-stats-bot",
            **({"Authorization": "Bearer %s" % TOKEN} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def graphql(query: str, variables: dict) -> dict | None:
    if not TOKEN:
        return None
    payload = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": "Bearer %s" % TOKEN,
            "Content-Type": "application/json",
            "User-Agent": "profile-stats-bot",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        print("graphql unavailable: http %d" % exc.code)
        return None
    if body.get("errors"):
        print("graphql errors: %s" % body["errors"])
        return None
    return body.get("data")


CALENDAR_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def contribution_stats() -> dict:
    data = graphql(CALENDAR_QUERY, {"login": USER})
    if not data or not data.get("user"):
        return {"total": None, "current": None, "longest": None}

    calendar = data["user"]["contributionsCollection"]["contributionCalendar"]
    days = [
        (date.fromisoformat(day["date"]), day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    days.sort()

    longest = run = 0
    for _day, count in days:
        run = run + 1 if count else 0
        longest = max(longest, run)

    # Today being empty does not break a streak; the day is not over yet.
    current = 0
    for day, count in reversed(days):
        if count:
            current += 1
        elif day == date.today():
            continue
        else:
            break

    return {"total": calendar["totalContributions"], "current": current, "longest": longest}


def language_mix(repos: list) -> list:
    totals: dict[str, int] = {}
    for repo in repos:
        if repo["fork"]:
            continue
        try:
            languages = api("/repos/%s/languages" % repo["full_name"])
        except Exception:
            continue
        for name, size in languages.items():
            totals[name] = totals.get(name, 0) + size

    grand = sum(totals.values())
    if not grand:
        return []

    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    top = ranked[:TOP_LANGS]
    mix = [(name, size / grand * 100) for name, size in top]
    remainder = 100 - sum(share for _n, share in mix)
    if remainder > 0.5:
        mix.append(("other", remainder))
    return mix


def tile(x: int, value: str, label: str) -> str:
    return """
  <rect class="card" x="{x}" y="54" width="193" height="76" rx="10"/>
  <rect class="stroke" x="{x}.5" y="54.5" width="192" height="75" rx="10"/>
  <text class="mono big accent" x="{cx}" y="94"  text-anchor="middle">{value}</text>
  <text class="mono sub muted" x="{cx}" y="114" text-anchor="middle">{label}</text>""".format(
        x=x, cx=x + 96, value=value, label=label
    )


def language_bar(mix: list) -> tuple[str, str]:
    segments = []
    legend = []
    cursor = 30.0

    for index, (name, share) in enumerate(mix):
        width = 820 * share / 100
        color = LANG_COLORS.get(name, FALLBACK_COLOR)
        # Overlap each segment slightly so no hairline gap shows between them.
        segments.append(
            '<rect x="%.2f" y="168" width="%.2f" height="12" fill="%s"/>' % (cursor, width + 0.6, color)
        )
        cursor += width

        legend_x = 30 + index * 118
        legend.append(
            '<circle cx="%d" cy="206" r="4" fill="%s"/>'
            '<text class="mono sub fg" x="%d" y="209">%s</text>'
            '<text class="mono sub muted" x="%d" y="209">%.1f%%</text>'
            % (legend_x + 4, color, legend_x + 14, name, legend_x + 14 + len(name) * 5.4 + 7, share)
        )

    return "\n    ".join(segments), "\n  ".join(legend)


TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="880" height="236" viewBox="0 0 880 236" role="img" aria-label="GitHub statistics">
  <title>By the numbers</title>
  <style>
    svg {{
      --bg: #ffffff;
      --card: #f6f8fa;
      --line: #d0d7de;
      --fg: #1f2328;
      --muted: #6e7781;
      --accent: #4b91f1;
      --track: #e6eaef;
    }}
    @media (prefers-color-scheme: dark) {{
      svg {{
        --bg: #0d1117;
        --card: #161b22;
        --line: #30363d;
        --fg: #e6edf3;
        --muted: #8b949e;
        --accent: #64a1f4;
        --track: #21262d;
      }}
    }}
    .bg     {{ fill: var(--bg); }}
    .card   {{ fill: var(--card); }}
    .stroke {{ stroke: var(--line); fill: none; }}
    .fg     {{ fill: var(--fg); }}
    .muted  {{ fill: var(--muted); }}
    .accent {{ fill: var(--accent); }}
    .track  {{ fill: var(--track); }}
    .mono   {{ font-family: ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }}
    .big    {{ font-size: 27px; font-weight: 700; }}
    .sub    {{ font-size: 8.5px; letter-spacing: 0.05em; }}
    .tiny   {{ font-size: 9px; letter-spacing: 0.08em; }}
  </style>

  <defs>
    <clipPath id="barClip"><rect x="30" y="168" width="820" height="12" rx="6"/></clipPath>
  </defs>

  <rect class="bg" x="0" y="0" width="880" height="236" rx="16"/>
  <rect class="stroke" x="0.5" y="0.5" width="879" height="235" rx="16"/>

  <text class="mono tiny muted" x="30" y="34">BY THE NUMBERS</text>
  <text class="mono tiny muted" x="850" y="34" text-anchor="end">GENERATED IN THIS REPO &#183; NO EXTERNAL CARDS</text>
{tiles}

  <text class="mono tiny muted" x="30" y="156">LANGUAGE MIX</text>
  <rect class="track" x="30" y="168" width="820" height="12" rx="6"/>
  <g clip-path="url(#barClip)">
    {bar}
  </g>
  {legend}
</svg>
"""


def main() -> None:
    profile = api("/users/%s" % USER)
    repos: list = []
    page = 1
    while True:
        batch = api("/users/%s/repos?per_page=100&page=%d" % (USER, page))
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    contributions = contribution_stats()
    mix = language_mix(repos)

    tiles = "".join(
        [
            tile(30, str(contributions["total"]) if contributions["total"] is not None else "--", "contributions this year"),
            tile(239, "%sd" % contributions["current"] if contributions["current"] is not None else "--", "current streak"),
            tile(448, "%sd" % contributions["longest"] if contributions["longest"] is not None else "--", "longest streak"),
            tile(657, str(profile["public_repos"]), "public repositories"),
        ]
    )

    bar, legend = language_bar(mix)
    SVG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SVG_FILE.write_text(TEMPLATE.format(tiles=tiles, bar=bar, legend=legend))

    print("contributions=%s current=%s longest=%s repos=%s" % (
        contributions["total"], contributions["current"], contributions["longest"], profile["public_repos"]))
    print("languages: %s" % ", ".join("%s %.1f%%" % (n, s) for n, s in mix))


if __name__ == "__main__":
    main()
