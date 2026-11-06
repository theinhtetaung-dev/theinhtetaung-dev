#!/usr/bin/env python3
"""Update the GitHub statistics embedded in the profile SVG assets."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


USERNAME = os.getenv("PROFILE_USERNAME", "theinhtetaung-dev")
TOKEN = os.getenv("GITHUB_TOKEN", "")
ROOT = Path(__file__).resolve().parents[1]
SVG_FILES = (
    ROOT / "assets" / "profile-light.svg",
    ROOT / "assets" / "profile-dark.svg",
)


def github_get(path: str) -> tuple[object, dict[str, str]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-stats-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(
        f"https://api.github.com{path}", headers=headers
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
            response_headers = {key.lower(): value for key, value in response.headers.items()}
            return data, response_headers
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned {error.code}: {details}") from error


def fetch_all_public_repositories() -> list[dict[str, object]]:
    repositories: list[dict[str, object]] = []
    page = 1
    while True:
        data, _ = github_get(
            f"/users/{USERNAME}/repos?type=owner&sort=full_name&per_page=100&page={page}"
        )
        if not isinstance(data, list):
            raise RuntimeError("Unexpected repositories response from GitHub API")
        repositories.extend(data)
        if len(data) < 100:
            return repositories
        page += 1


def collect_stats() -> dict[str, int]:
    user, _ = github_get(f"/users/{USERNAME}")
    if not isinstance(user, dict):
        raise RuntimeError("Unexpected user response from GitHub API")

    repositories = fetch_all_public_repositories()
    return {
        "Repos": int(user["public_repos"]),
        "Stars": sum(int(repo.get("stargazers_count", 0)) for repo in repositories),
        "Forks": sum(int(repo.get("forks_count", 0)) for repo in repositories),
        "Followers": int(user["followers"]),
        "Following": int(user["following"]),
    }


def update_svg(path: Path, stats: dict[str, int]) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original

    for label, value in stats.items():
        pattern = re.compile(
            rf'(<tspan class="key">{re.escape(label)}</tspan>:\s*'
            rf'<tspan class="value">)[\d,]+(</tspan>)'
        )
        updated, replacements = pattern.subn(
            rf"\g<1>{value:,}\g<2>", updated, count=1
        )
        if replacements != 1:
            raise RuntimeError(f"Could not update {label!r} in {path}")

    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    stats = collect_stats()
    print("Fetched GitHub statistics:")
    for label, value in stats.items():
        print(f"  {label}: {value:,}")

    changed = []
    for svg_file in SVG_FILES:
        if not svg_file.exists():
            raise FileNotFoundError(svg_file)
        if update_svg(svg_file, stats):
            changed.append(svg_file.relative_to(ROOT))

    if changed:
        print("Updated: " + ", ".join(map(str, changed)))
    else:
        print("Profile statistics are already current.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
