#!/usr/bin/env python3
"""Generate the repository snapshot consumed by the projects page."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


OWNER = "fengjutian"
OUTPUT = Path(__file__).resolve().parents[1] / "_data" / "github_repositories.json"
API_URL = f"https://api.github.com/users/{OWNER}/repos"


def fetch_page(page: int) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "per_page": 100,
            "page": page,
            "sort": "pushed",
            "direction": "desc",
            "type": "owner",
        }
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "fengjutian.github.io repository sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(f"{API_URL}?{query}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_all() -> list[dict]:
    repositories: list[dict] = []
    page = 1
    while True:
        items = fetch_page(page)
        repositories.extend(items)
        if len(items) < 100:
            return repositories
        page += 1


def normalize(repository: dict) -> dict:
    return {
        "name": repository["name"],
        "description": repository.get("description") or "暂无项目描述。",
        "url": repository["html_url"],
        "homepage": repository.get("homepage") or "",
        "language": repository.get("language") or "未标注",
        "fork": bool(repository.get("fork")),
        "archived": bool(repository.get("archived")),
        "stars": int(repository.get("stargazers_count", 0)),
        "created_at": repository["created_at"],
        "pushed_at": repository.get("pushed_at") or repository["updated_at"],
    }


def main() -> int:
    try:
        repositories = [normalize(repository) for repository in fetch_all()]
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"Failed to fetch GitHub repositories: {error}", file=sys.stderr)
        return 1

    repositories.sort(key=lambda repository: repository["pushed_at"], reverse=True)
    payload = {
        "owner": OWNER,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": len(repositories),
        "original_count": sum(not repository["fork"] for repository in repositories),
        "fork_count": sum(repository["fork"] for repository in repositories),
        "repositories": repositories,
    }
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {payload['total']} repositories "
        f"({payload['original_count']} original, {payload['fork_count']} forks) to {OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
