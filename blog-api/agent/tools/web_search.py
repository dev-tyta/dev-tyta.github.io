"""
Web search tool — Tavily primary, DuckDuckGo fallback.
Used to ground answers about external topics and verify facts.
"""

import os
from typing import Optional

import httpx
from langchain_core.tools import tool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def _tavily_search(query: str, max_results: int = 4) -> Optional[str]:
    """Call Tavily Search API."""
    if not TAVILY_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            res = await client.post(
                "https://api.tavily.com/search",
                json={"api_key": TAVILY_API_KEY, "query": query, "max_results": max_results, "search_depth": "basic"},
            )
            if res.status_code != 200:
                return None
            data = res.json()
            results = data.get("results", [])
            if not results:
                return None
            lines = [f"- [{r['title']}]({r['url']}): {r.get('content','')[:200]}" for r in results]
            return "**Web search results (Tavily):**\n" + "\n".join(lines)
    except Exception:
        return None


async def _ddg_search(query: str) -> str:
    """DuckDuckGo instant answer fallback."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_redirect": "1", "no_html": "1"},
                headers={"User-Agent": "testimony-portfolio-agent/1.0"},
            )
            data = res.json()
            abstract = data.get("AbstractText", "")
            source = data.get("AbstractURL", "")
            if abstract:
                return f"**Web search result (DDG):**\n{abstract}\nSource: {source}"
            # Try related topics
            topics = data.get("RelatedTopics", [])[:3]
            if topics:
                lines = [t.get("Text", "") for t in topics if isinstance(t, dict) and t.get("Text")]
                return "**Related information:**\n" + "\n".join(f"- {l}" for l in lines)
            return "No results found for that query."
    except Exception as e:
        return f"Search unavailable: {str(e)[:100]}"


@tool
async def search_web(query: str) -> str:
    """
    Search the web to get current information or verify facts about external topics.
    Use for: technical concepts Testimony references, recent AI research, industry news,
    or any fact that might need external verification.
    Input: a specific search query string.
    """
    result = await _tavily_search(query)
    if result:
        return result
    return await _ddg_search(query)
