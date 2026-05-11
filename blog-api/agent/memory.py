"""
Redis-backed conversation memory.
Each session has a 24-hr TTL that refreshes on every message.
"""

import json
import os
from typing import Optional

import redis.asyncio as aioredis
from langchain_community.chat_message_histories import RedisChatMessageHistory

REDIS_URL = os.environ["REDIS_URL"]
SESSION_TTL = int(os.getenv("SESSION_TTL_SECONDS", 86400))   # 24 hours default
MSG_HISTORY_PREFIX = "agent:chat:"
SESSION_INDEX_KEY = "agent:sessions"


def get_message_history(session_id: str) -> RedisChatMessageHistory:
    """Return a LangChain-compatible chat history for this session."""
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=SESSION_TTL,
        key_prefix=MSG_HISTORY_PREFIX,
    )


async def count_active_sessions(r: aioredis.Redis) -> int:
    """Count sessions that have keys in Redis (approximate)."""
    keys = await r.keys(f"{MSG_HISTORY_PREFIX}*")
    return len(keys)


async def clear_session(session_id: str, r: aioredis.Redis) -> None:
    """Manually clear a session's history."""
    key = f"{MSG_HISTORY_PREFIX}{session_id}"
    await r.delete(key)


async def refresh_ttl(session_id: str, r: aioredis.Redis) -> None:
    """Reset the TTL on every interaction so active sessions don't expire."""
    key = f"{MSG_HISTORY_PREFIX}{session_id}"
    await r.expire(key, SESSION_TTL)
