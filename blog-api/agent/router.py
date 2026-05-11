"""
FastAPI router for the agent chat API.
Parses [NAV:url|label] and [QR:text] markers from agent responses.
"""

import re
import uuid
from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .core import get_agent
from .memory import clear_session, count_active_sessions
from .monitoring import active_sessions

router = APIRouter(prefix="/agent", tags=["agent"])

# ── Marker parsing ─────────────────────────────────────────────────────────────
_NAV_RE = re.compile(r'\[NAV:([^\|]+)\|([^\]]+)\]', re.IGNORECASE)
_QR_RE  = re.compile(r'\[QR:([^\]]+)\]', re.IGNORECASE)


def _parse_response(raw: str) -> tuple[str, Optional[str], Optional[str], list[str]]:
    """
    Extract [NAV:url|label] and [QR:text] markers.
    Returns: (clean_reply, navigate_url, navigate_label, quick_replies)
    """
    navigate_url = navigate_label = None
    quick_replies: list[str] = []

    nav_match = _NAV_RE.search(raw)
    if nav_match:
        navigate_url   = nav_match.group(1).strip()
        navigate_label = nav_match.group(2).strip()
        raw = raw[:nav_match.start()] + raw[nav_match.end():]

    for qr in _QR_RE.finditer(raw):
        quick_replies.append(qr.group(1).strip())
    raw = _QR_RE.sub('', raw).strip()

    return raw, navigate_url, navigate_label, quick_replies


# ── Models ─────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id:   str = Field(..., min_length=8, max_length=128)
    message:      str = Field(..., min_length=1, max_length=4000)
    current_page: str = Field("", max_length=256)  # e.g. "/projects/mmibc.html"

class ChatResponseModel(BaseModel):
    session_id:     str
    reply:          str
    model_used:     str
    is_fallback:    bool
    tool_calls:     list[str]
    navigate_url:   Optional[str] = None
    navigate_label: Optional[str] = None
    quick_replies:  list[str] = []

class SessionResponse(BaseModel):
    session_id: str

class HealthResponse(BaseModel):
    status:          str
    models:          dict
    active_sessions: int


# ── Routes ──────────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponseModel)
async def chat(req: ChatRequest, request: Request):
    """Send a message to Testimony's digital double."""
    r: aioredis.Redis = request.app.state.redis
    agent = get_agent(r)

    # Inject current page as context prefix so agent knows where the user is
    message = req.message
    if req.current_page:
        message = f"[User is currently on page: {req.current_page}]\n{req.message}"

    result = await agent.chat(session_id=req.session_id, message=message, redis=r)

    if result.error == "no_llm_available":
        raise HTTPException(status_code=503, detail="Agent temporarily unavailable")

    clean, nav_url, nav_label, qrs = _parse_response(result.reply)

    return ChatResponseModel(
        session_id=result.session_id,
        reply=clean,
        model_used=result.model_used,
        is_fallback=result.is_fallback,
        tool_calls=result.tool_calls,
        navigate_url=nav_url,
        navigate_label=nav_label,
        quick_replies=qrs,
    )


@router.post("/session", response_model=SessionResponse)
async def new_session():
    return SessionResponse(session_id=str(uuid.uuid4()))


@router.delete("/session/{session_id}")
async def end_session(session_id: str, request: Request):
    r: aioredis.Redis = request.app.state.redis
    await clear_session(session_id, r)
    return {"ok": True}


@router.get("/health", response_model=HealthResponse)
async def agent_health(request: Request):
    r: aioredis.Redis = request.app.state.redis
    agent = get_agent(r)
    n = await count_active_sessions(r)
    active_sessions.set(n)
    return HealthResponse(status="ok", models=agent.models_available, active_sessions=n)
