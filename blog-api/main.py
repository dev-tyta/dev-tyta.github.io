"""
Blog API — FastAPI + Redis
Env vars required:
  REDIS_URL, GITHUB_PAT, GITHUB_OWNER, GITHUB_REPO, ALLOWED_ORIGIN
Agent extras (optional):
  GOOGLE_API_KEY, GROQ_API_KEY, TAVILY_API_KEY, LANGCHAIN_API_KEY
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, CONTACT_EMAIL
  GEMINI_MODEL, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
"""

import base64
import hashlib
import json
import os
import secrets
from typing import List, Optional

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

# ── Config ────────────────────────────────────────────────────────────────────
REDIS_URL      = os.environ["REDIS_URL"]
GITHUB_PAT     = os.environ["GITHUB_PAT"]
GITHUB_OWNER   = os.getenv("GITHUB_OWNER", "dev-tyta")
GITHUB_REPO    = os.getenv("GITHUB_REPO", "dev-tyta.github.io")
POSTS_PATH     = os.getenv("POSTS_PATH", "data/posts.json")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "https://dev-tyta.github.io")
SESSION_TTL    = 60 * 60 * 12  # 12 hours

# Redis keys
K_ADMIN_HASH = "blog:admin_hash"
K_SESSIONS   = "blog:sessions"
K_POSTS      = "blog:posts"

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Testimony Portfolio API", docs_url="/docs", redoc_url=None)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://dev-tyta.github.io",
        "null",  # Dev only: allows file:// protocol access
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup / shutdown ─────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    from agent.monitoring import configure_langsmith
    from agent.router import router as agent_router
    configure_langsmith()
    app.include_router(agent_router)
    # Shared Redis pool stored on app.state for agent router dependency
    app.state.redis = aioredis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, "redis"):
        await app.state.redis.aclose()

# ── Redis pool (blog endpoints) ───────────────────────────────────────────────
_redis: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

# ── Models ────────────────────────────────────────────────────────────────────
class AuthRequest(BaseModel):
    password: str

class Post(BaseModel):
    id: str
    title: str
    date: str
    readTime: str = "5 min"
    category: str
    featured: bool = False
    tags: List[str] = []
    excerpt: str
    content: str
    published: bool = True

# ── Helpers ───────────────────────────────────────────────────────────────────
def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

async def _require_session(token: str) -> None:
    r = await get_redis()
    if not await r.sismember(K_SESSIONS, token):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

async def _github_commit(posts: list[dict], message: str) -> None:
    """Read current file SHA, update content, commit."""
    api_base = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{POSTS_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        # Get current SHA
        get_res = await client.get(api_base, headers=headers)
        if get_res.status_code not in (200, 404):
            raise HTTPException(status_code=502, detail=f"GitHub GET failed: {get_res.status_code}")

        sha = get_res.json().get("sha") if get_res.status_code == 200 else None
        encoded = base64.b64encode(json.dumps(posts, indent=2).encode()).decode()

        body: dict = {"message": message, "content": encoded}
        if sha:
            body["sha"] = sha

        put_res = await client.put(api_base, headers=headers, json=body)
        if put_res.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail=f"GitHub commit failed: {put_res.status_code} {put_res.text[:200]}")

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Welcome to the Testimony Portfolio API. Visit /docs for API documentation."}

@app.get("/health")
async def health():
    r = await get_redis()
    await r.ping()
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    from agent.monitoring import metrics_response
    return metrics_response()

@app.get("/posts")
async def list_posts():
    r = await get_redis()
    raw = await r.get(K_POSTS)

    if not raw:
        # Auto-seed from static file on first run
        static_path = os.path.join(os.path.dirname(__file__), "..", "data", "posts.json")
        if os.path.exists(static_path):
            with open(static_path, "r") as f:
                seed = f.read()
            await r.set(K_POSTS, seed)
            posts = json.loads(seed)
        else:
            return []
    else:
        posts = json.loads(raw)

    return [p for p in posts if p.get("published", True)]

@app.post("/auth")
async def authenticate(req: AuthRequest):
    r = await get_redis()
    stored = await r.get(K_ADMIN_HASH)
    first_time = stored is None

    if first_time:
        if len(req.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        await r.set(K_ADMIN_HASH, _sha256(req.password))
    else:
        if _sha256(req.password) != stored:
            raise HTTPException(status_code=401, detail="Incorrect password")

    token = secrets.token_urlsafe(32)
    await r.sadd(K_SESSIONS, token)
    await r.expire(K_SESSIONS, SESSION_TTL)
    return {"token": token, "first_time": first_time}

@app.delete("/auth")
async def logout(x_session_token: str = Header(...)):
    r = await get_redis()
    await r.srem(K_SESSIONS, x_session_token)
    return {"ok": True}

@app.post("/posts")
async def create_post(post: Post, x_session_token: str = Header(...)):
    await _require_session(x_session_token)
    r = await get_redis()

    raw = await r.get(K_POSTS)
    posts: list[dict] = json.loads(raw) if raw else []

    if any(p["id"] == post.id for p in posts):
        raise HTTPException(status_code=409, detail=f"Post '{post.id}' already exists. Change the title.")

    new_post = post.model_dump()
    posts.insert(0, new_post)
    await r.set(K_POSTS, json.dumps(posts))

    # Commit to GitHub so the static fetch fallback also works
    try:
        await _github_commit(posts, f'blog: add "{post.title}"')
        committed = True
    except HTTPException:
        committed = False  # Stored in Redis, GitHub commit failed — not fatal

    return {"ok": True, "id": post.id, "github_committed": committed}
