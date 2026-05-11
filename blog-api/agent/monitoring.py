"""
Model monitoring — Prometheus metrics + structured logging.
Exposes /metrics endpoint for scraping.
LangSmith tracing via env var LANGCHAIN_TRACING_V2=true.
"""

import logging
import os
import time
from contextlib import contextmanager
from typing import Optional

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# ── Structured logger ─────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":%(message)s}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("agent")

# ── Prometheus metrics ─────────────────────────────────────────────────────────
_PREFIX = "testimony_agent"

requests_total = Counter(
    f"{_PREFIX}_requests_total",
    "Total chat requests",
    ["model", "status"],         # status: success | error | fallback
)

latency_seconds = Histogram(
    f"{_PREFIX}_latency_seconds",
    "End-to-end chat latency",
    ["model"],
    buckets=[0.5, 1, 2, 4, 8, 15, 30, 60],
)

tokens_used = Counter(
    f"{_PREFIX}_tokens_total",
    "LLM tokens consumed",
    ["model", "type"],           # type: prompt | completion
)

tool_calls_total = Counter(
    f"{_PREFIX}_tool_calls_total",
    "Tool invocations",
    ["tool_name", "status"],     # status: ok | error
)

fallback_events = Counter(
    f"{_PREFIX}_fallback_total",
    "Times the fallback model was used",
)

active_sessions = Gauge(
    f"{_PREFIX}_active_sessions",
    "Number of active chat sessions in Redis",
)

errors_total = Counter(
    f"{_PREFIX}_errors_total",
    "Unhandled errors",
    ["error_type"],
)


# ── Context managers ───────────────────────────────────────────────────────────
@contextmanager
def track_request(model: str):
    """Track latency and success/failure for one chat request."""
    start = time.perf_counter()
    status = "success"
    try:
        yield
    except Exception as exc:
        status = "error"
        errors_total.labels(error_type=type(exc).__name__).inc()
        raise
    finally:
        elapsed = time.perf_counter() - start
        requests_total.labels(model=model, status=status).inc()
        latency_seconds.labels(model=model).observe(elapsed)
        logger.info(f'"event":"request_complete","model":"{model}","status":"{status}","latency_s":{elapsed:.3f}')


def record_tokens(model: str, prompt_tokens: int, completion_tokens: int) -> None:
    tokens_used.labels(model=model, type="prompt").inc(prompt_tokens)
    tokens_used.labels(model=model, type="completion").inc(completion_tokens)


def record_tool(tool_name: str, ok: bool = True) -> None:
    tool_calls_total.labels(tool_name=tool_name, status="ok" if ok else "error").inc()


def record_fallback() -> None:
    fallback_events.inc()
    logger.warning('"event":"fallback_activated","reason":"primary_llm_failed"')


# ── FastAPI route ──────────────────────────────────────────────────────────────
def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ── LangSmith setup ───────────────────────────────────────────────────────────
def configure_langsmith() -> None:
    """
    Enable LangSmith tracing only when LANGCHAIN_TRACING_V2=true is explicitly set
    AND a valid LANGCHAIN_API_KEY is present. Auto-enable is disabled to prevent
    noisy 403 warnings from invalid/expired keys.
    """
    key      = os.getenv("LANGCHAIN_API_KEY")
    explicit = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    if key and explicit:
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "testimony-portfolio-agent")
        logger.info('"event":"langsmith_enabled","project":"%s"', os.environ["LANGCHAIN_PROJECT"])
    else:
        # Disable tracing so LangSmith client never fires — no 403 noise
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        reason = "no_api_key" if not key else "not_explicitly_enabled"
        logger.info('"event":"langsmith_disabled","reason":"%s"', reason)
