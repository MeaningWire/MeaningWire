#!/usr/bin/env python3
"""Experimental read-only GitHub repository adapter for MeaningWire.

This adapter intentionally emits an adapter-local experimental envelope rather than a
stable MeaningWire canonical contract. Canonical schemas are still under design.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

GITHUB_API_VERSION = "2022-11-28"
ADAPTER_OUTPUT = "github.repository.snapshot.v0"
_REPOSITORY_SLUG = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class GitHubAdapterError(RuntimeError):
    """Raised when the GitHub adapter cannot retrieve or normalize a repository."""


def validate_repository_slug(repository: str) -> str:
    repository = repository.strip()
    if not _REPOSITORY_SLUG.fullmatch(repository):
        raise GitHubAdapterError("repository must use owner/name form")
    return repository


def build_repository_url(repository: str) -> str:
    repository = validate_repository_slug(repository)
    return f"https://api.github.com/repos/{repository}"


def fetch_repository(repository: str, token: str | None = None) -> dict[str, Any]:
    url = build_repository_url(repository)
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MeaningWire-GitHub-Reference-Adapter/0",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise GitHubAdapterError(f"GitHub API returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise GitHubAdapterError(f"GitHub API request failed: {exc.reason}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GitHubAdapterError("GitHub API returned an invalid JSON response") from exc

    if not isinstance(payload, dict):
        raise GitHubAdapterError("GitHub API repository response must be an object")
    return payload


def normalize_repository(payload: dict[str, Any], *, retrieved_at: str | None = None) -> dict[str, Any]:
    full_name = payload.get("full_name")
    html_url = payload.get("html_url")
    api_url = payload.get("url")
    if not isinstance(full_name, str) or not full_name:
        raise GitHubAdapterError("GitHub repository response is missing full_name")
    if not isinstance(html_url, str) or not html_url:
        raise GitHubAdapterError("GitHub repository response is missing html_url")
    if not isinstance(api_url, str) or not api_url:
        raise GitHubAdapterError("GitHub repository response is missing url")

    timestamp = retrieved_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    owner = payload.get("owner") if isinstance(payload.get("owner"), dict) else {}

    return {
        "adapter_output": ADAPTER_OUTPUT,
        "maturity": "experimental",
        "source": {
            "system": "github",
            "resource_type": "repository",
            "api_version": GITHUB_API_VERSION,
            "api_url": api_url,
            "web_url": html_url,
            "retrieved_at": timestamp,
        },
        "repository": {
            "source_id": payload.get("id"),
            "node_id": payload.get("node_id"),
            "full_name": full_name,
            "name": payload.get("name"),
            "owner_login": owner.get("login"),
            "description": payload.get("description"),
            "visibility": payload.get("visibility"),
            "private": payload.get("private"),
            "archived": payload.get("archived"),
            "default_branch": payload.get("default_branch"),
            "language": payload.get("language"),
            "license_spdx_id": (
                payload.get("license", {}).get("spdx_id")
                if isinstance(payload.get("license"), dict)
                else None
            ),
            "topics": payload.get("topics") if isinstance(payload.get("topics"), list) else [],
            "created_at": payload.get("created_at"),
            "updated_at": payload.get("updated_at"),
            "pushed_at": payload.get("pushed_at"),
        },
        "mapping": {
            "status": "adapter-local",
            "canonical_contract": None,
            "note": "Canonical MeaningWire repository semantics are not yet stable.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch a GitHub repository and emit an experimental MeaningWire adapter record."
    )
    parser.add_argument("repository", help="GitHub repository in owner/name form")
    parser.add_argument(
        "--token-env",
        default="GITHUB_TOKEN",
        help="environment variable containing an optional GitHub token (default: GITHUB_TOKEN)",
    )
    args = parser.parse_args(argv)

    try:
        payload = fetch_repository(args.repository, token=os.getenv(args.token_env))
        normalized = normalize_repository(payload)
    except GitHubAdapterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(normalized, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
