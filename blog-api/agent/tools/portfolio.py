"""
Portfolio tool — fetches live data from Testimony's portfolio:
blog posts from Redis/JSON, and structured section content.
"""

import json
import os
from typing import Optional

import httpx
import redis.asyncio as aioredis
from langchain_core.tools import tool

REDIS_URL = os.environ["REDIS_URL"]
PORTFOLIO_BASE = "https://dev-tyta.github.io"
K_POSTS = "blog:posts"

_redis: Optional[aioredis.Redis] = None


async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


@tool
async def get_blog_posts(topic: str = "") -> str:
    """
    Retrieve Testimony's blog posts. Optionally filter by topic keyword.
    Use when asked about what Testimony has written, his technical writing, or specific topics he's covered.
    Input: optional topic keyword to filter (empty string returns all posts).
    """
    r = await _get_redis()
    raw = await r.get(K_POSTS)
    if raw:
        posts = json.loads(raw)
    else:
        # Fallback: fetch from static file
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                res = await client.get(f"{PORTFOLIO_BASE}/data/posts.json")
                posts = res.json() if res.status_code == 200 else []
        except Exception:
            posts = []

    if not posts:
        return "No blog posts found."

    published = [p for p in posts if p.get("published", True)]
    if topic:
        kw = topic.lower()
        published = [
            p for p in published
            if kw in p.get("title", "").lower()
            or kw in p.get("excerpt", "").lower()
            or kw in " ".join(p.get("tags", [])).lower()
            or kw in p.get("category", "").lower()
        ]

    if not published:
        return f"No posts found matching '{topic}'."

    lines = []
    for p in published[:8]:
        tags = ", ".join(p.get("tags", []))
        lines.append(
            f"**{p['title']}** ({p.get('date','')} · {p.get('readTime','')})  \n"
            f"Category: {p.get('category','')} | Tags: {tags}  \n"
            f"{p.get('excerpt','')}  \n"
            f"Read: {PORTFOLIO_BASE}/post.html?post={p['id']}"
        )

    return f"Found {len(published)} post(s):\n\n" + "\n\n---\n\n".join(lines)


@tool
async def get_portfolio_section(section: str) -> str:
    """
    Fetch a live section of Testimony's portfolio for current, accurate data.
    Valid sections: 'now', 'projects', 'research', 'skills', 'experience', 'community'
    Use when you need the most up-to-date version of any portfolio section.
    Input: section name string.
    """
    section_urls = {
        "now": f"{PORTFOLIO_BASE}/now.html",
        "projects": f"{PORTFOLIO_BASE}/index.html#projects",
        "research": f"{PORTFOLIO_BASE}/index.html#research",
        "skills": f"{PORTFOLIO_BASE}/index.html#skills",
        "experience": f"{PORTFOLIO_BASE}/index.html#experience",
        "community": f"{PORTFOLIO_BASE}/index.html#community",
        "mmibc": f"{PORTFOLIO_BASE}/projects/mmibc.html",
        "afrivton": f"{PORTFOLIO_BASE}/projects/afrivton.html",
    }

    clean = section.lower().strip()
    url = section_urls.get(clean)
    if not url:
        available = ", ".join(section_urls.keys())
        return f"Unknown section '{section}'. Available: {available}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url)
            if res.status_code != 200:
                return f"[Portfolio] Could not fetch section '{section}' (HTTP {res.status_code})"

        # Strip HTML tags simply (no BS4 dep)
        import re
        text = re.sub(r"<script[^>]*>.*?</script>", " ", res.text, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s{3,}", "\n", text).strip()
        # Return first 2500 chars — enough for context without flooding
        return f"[Live portfolio section: {section}]\n{text[:2500]}"
    except Exception as e:
        return f"[Portfolio] Error fetching section: {str(e)[:100]}"
