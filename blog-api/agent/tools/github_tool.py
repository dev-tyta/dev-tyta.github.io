"""GitHub tool — fetches public repo and profile data for dev-tyta."""

import os
from typing import Optional

import httpx
from langchain_core.tools import tool

GITHUB_USER = "dev-tyta"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")   # optional — raises rate limit to 5000/hr
_HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    _HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"


@tool
async def search_github(query: str) -> str:
    """
    Search Testimony's GitHub profile for repositories, activity, or project details.
    Use when asked about specific repos, recent code activity, or tech stack in use.
    Input: a natural-language question or repo name.
    """
    async with httpx.AsyncClient(timeout=10, headers=_HEADERS) as client:
        # Fetch user profile
        profile_res = await client.get(f"https://api.github.com/users/{GITHUB_USER}")
        if profile_res.status_code != 200:
            return f"[GitHub] Could not fetch profile (HTTP {profile_res.status_code})"

        profile = profile_res.json()

        # Fetch repos sorted by recent activity
        repos_res = await client.get(
            f"https://api.github.com/users/{GITHUB_USER}/repos",
            params={"sort": "updated", "per_page": 12, "type": "public"},
        )
        repos = repos_res.json() if repos_res.status_code == 200 else []

    if not isinstance(repos, list):
        repos = []

    repo_lines = []
    for r in repos[:10]:
        lang = r.get("language") or "—"
        stars = r.get("stargazers_count", 0)
        desc = r.get("description") or ""
        updated = (r.get("updated_at") or "")[:10]
        repo_lines.append(
            f"- **{r['name']}** ({lang}, ★{stars}) — {desc} [updated {updated}]"
        )

    result = (
        f"**GitHub Profile for {GITHUB_USER}**\n"
        f"Public repos: {profile.get('public_repos', '?')} | "
        f"Followers: {profile.get('followers', '?')} | "
        f"Following: {profile.get('following', '?')}\n"
        f"Bio: {profile.get('bio') or 'N/A'}\n\n"
        f"**Recent Repositories:**\n"
        + "\n".join(repo_lines)
        + f"\n\nSource: https://github.com/{GITHUB_USER}"
    )
    return result
