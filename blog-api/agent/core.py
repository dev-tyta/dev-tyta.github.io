"""
Agent core — LangGraph create_react_agent (LangChain 1.x compatible).
Primary: Gemini 1.5 Flash. Fallback: Groq llama-3.1-8b-instant.
Memory: manual Redis injection — history loaded before call, saved after.
No AgentExecutor (removed in LangChain 1.x).
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Optional

import redis.asyncio as aioredis
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from .memory import refresh_ttl
from .monitoring import record_fallback, record_tool, track_request
from .prompts import SYSTEM_PROMPT
from .tools.contact_email import send_contact_message
from .tools.github_tool import search_github
from .tools.portfolio import get_blog_posts, get_portfolio_section
from .tools.web_search import search_web

log = logging.getLogger("agent.core")

REDIS_URL        = os.environ["REDIS_URL"]
HISTORY_PREFIX   = "agent:chat:"
HISTORY_TTL      = int(os.getenv("SESSION_TTL_SECONDS", "86400"))
MAX_HISTORY_MSGS = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

ALL_TOOLS = [search_github, get_blog_posts, get_portfolio_section, search_web, send_contact_message]


def _build_gemini():
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        google_api_key=os.environ["GOOGLE_API_KEY"],
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
        max_output_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        top_p=0.85,
    )


def _build_groq():
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        groq_api_key=os.environ["GROQ_API_KEY"],
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
    )


@dataclass
class ChatResponse:
    reply: str
    model_used: str
    session_id: str
    is_fallback: bool = False
    tool_calls: list[str] = field(default_factory=list)
    error: Optional[str] = None


class TestimonyAgent:
    def __init__(self):
        self._primary  = None
        self._fallback = None
        self._init_agents()

    def _init_agents(self) -> None:
        if os.getenv("GOOGLE_API_KEY"):
            try:
                self._primary = create_react_agent(
                    model=_build_gemini(),
                    tools=ALL_TOOLS,
                    prompt=SYSTEM_PROMPT,
                )
                log.info("Gemini agent ready")
            except Exception as e:
                log.warning(f"Gemini init failed: {e}")

        if os.getenv("GROQ_API_KEY"):
            try:
                self._fallback = create_react_agent(
                    model=_build_groq(),
                    tools=ALL_TOOLS,
                    prompt=SYSTEM_PROMPT,
                )
                log.info("Groq fallback agent ready")
            except Exception as e:
                log.warning(f"Groq init failed: {e}")

        if not self._primary and not self._fallback:
            raise RuntimeError("No LLM available — set GOOGLE_API_KEY or GROQ_API_KEY.")

    def _load_history(self, session_id: str):
        try:
            hist = RedisChatMessageHistory(
                session_id=session_id,
                url=REDIS_URL,
                ttl=HISTORY_TTL,
                key_prefix=HISTORY_PREFIX,
            )
            return hist.messages[-MAX_HISTORY_MSGS:], hist
        except Exception as e:
            log.warning(f"History load failed {session_id}: {e}")
            return [], None

    def _save_exchange(self, hist, user_msg: str, ai_reply: str) -> None:
        try:
            if hist:
                hist.add_user_message(user_msg)
                hist.add_ai_message(ai_reply)
        except Exception as e:
            log.warning(f"History save failed: {e}")

    async def _invoke(self, agent, messages: list) -> tuple[str, list[str]]:
        result = await agent.ainvoke({"messages": messages})
        all_msgs = result.get("messages", [])

        reply = ""
        for msg in reversed(all_msgs):
            if isinstance(msg, AIMessage) and msg.content:
                c = msg.content
                if isinstance(c, str):
                    reply = c
                elif isinstance(c, list):
                    # Gemini returns [{"type":"text","text":"..."}]
                    reply = " ".join(p.get("text","") if isinstance(p, dict) else str(p) for p in c).strip()
                else:
                    reply = str(c)
                break

        tool_names = []
        for msg in all_msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
                    if name:
                        tool_names.append(name)
                        record_tool(name, ok=True)

        return reply or "I'm not sure how to respond — could you rephrase?", tool_names

    async def chat(self, session_id: str, message: str, redis: aioredis.Redis) -> ChatResponse:
        await refresh_ttl(session_id, redis)
        stored_msgs, hist = self._load_history(session_id)
        input_messages = stored_msgs + [HumanMessage(content=message)]

        if self._primary:
            try:
                with track_request("gemini"):
                    reply, tools = await self._invoke(self._primary, input_messages)
                self._save_exchange(hist, message, reply)
                return ChatResponse(reply=reply, model_used="gemini", session_id=session_id, tool_calls=tools)
            except Exception as e:
                log.warning(f"Gemini failed → Groq: {e}")
                record_fallback()

        if self._fallback:
            with track_request("groq"):
                reply, tools = await self._invoke(self._fallback, input_messages)
            self._save_exchange(hist, message, reply)
            return ChatResponse(reply=reply, model_used="groq", session_id=session_id, is_fallback=True, tool_calls=tools)

        return ChatResponse(
            reply="I'm temporarily unavailable. Email testimonyadekoya.02@gmail.com",
            model_used="none", session_id=session_id, error="no_llm_available",
        )

    @property
    def models_available(self) -> dict:
        return {
            "primary":  "gemini" if self._primary  else None,
            "fallback": "groq"   if self._fallback else None,
        }


_agent: Optional[TestimonyAgent] = None

def get_agent(redis_client: aioredis.Redis) -> TestimonyAgent:
    global _agent
    if _agent is None:
        _agent = TestimonyAgent()
    return _agent
