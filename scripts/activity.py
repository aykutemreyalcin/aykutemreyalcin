#!/usr/bin/env python3
"""Rewrite the activity block in the README from my public GitHub events."""

from __future__ import annotations

import json
import os
import pathlib
import re
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

USER = os.environ.get("GITHUB_ACTOR", "aykutemreyalcin")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
LIMIT = 5

START = "<!-- pulse:activity:start -->"
END = "<!-- pulse:activity:end -->"


def fetch_events() -> list:
    request = urllib.request.Request(
        "https://api.github.com/users/%s/events/public?per_page=100" % USER,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-activity-bot",
            **({"Authorization": "Bearer %s" % TOKEN} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def ago(iso: str) -> str:
    moment = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    seconds = (datetime.now(timezone.utc) - moment).total_seconds()
    for size, unit in ((86400, "d"), (3600, "h"), (60, "m")):
        if seconds >= size:
            return "%d%s ago" % (seconds // size, unit)
    return "just now"


def describe(event: dict) -> str | None:
    kind = event["type"]
    repo = event["repo"]["name"]
    link = "[`%s`](https://github.com/%s)" % (repo.split("/")[-1], repo)
    payload = event.get("payload", {})

    if kind == "PushEvent":
        count = payload.get("size", 0)
        if not count:
            return None
        return "pushed %d commit%s to %s" % (count, "" if count == 1 else "s", link)
    if kind == "CreateEvent":
        ref_type = payload.get("ref_type")
        if ref_type == "repository":
            return "created %s" % link
        if ref_type in ("branch", "tag"):
            return "created %s `%s` on %s" % (ref_type, payload.get("ref"), link)
        return None
    if kind == "PullRequestEvent":
        number = payload.get("number")
        action = payload.get("action")
        if action == "closed" and payload.get("pull_request", {}).get("merged"):
            action = "merged"
        return "%s pull request #%s in %s" % (action, number, link)
    if kind == "IssuesEvent":
        return "%s issue #%s in %s" % (payload.get("action"), payload.get("issue", {}).get("number"), link)
    if kind == "ReleaseEvent":
        return "released `%s` of %s" % (payload.get("release", {}).get("tag_name"), link)
    if kind == "WatchEvent":
        return "starred %s" % link
    if kind == "ForkEvent":
        return "forked %s" % link
    if kind == "PublicEvent":
        return "made %s public" % link
    return None


def main() -> None:
    lines: list[str] = []
    seen: set[str] = set()

    for event in fetch_events():
        text = describe(event)
        if not text or text in seen:
            continue
        seen.add(text)
        lines.append("- `%s` %s" % (ago(event["created_at"]).rjust(8), text))
        if len(lines) == LIMIT:
            break

    if not lines:
        lines = ["- nothing public in the last few days, heads down on private work"]

    body = "\n".join(lines)
    content = README.read_text()
    replaced = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        "%s\n%s\n%s" % (START, body, END),
        content,
        flags=re.DOTALL,
    )

    if replaced == content:
        print("activity block unchanged")
        return

    README.write_text(replaced)
    print("activity block updated:\n%s" % body)


if __name__ == "__main__":
    main()
