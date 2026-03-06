from fastapi import FastAPI, Request, Response, HTTPException, Header
import os

app = FastAPI(title="XNAi Forward-Auth Service")

# Simple API Key storage for internal agents
# In production, this would move to PostgreSQL or Redis
INTERNAL_AGENTS = {
    os.getenv("AGENT_ADMIN_KEY", "xnai-admin-secret-2026"): {
        "user": "admin",
        "email": "admin@xoe-novai.local",
        "groups": "admins,agents"
    },
    os.getenv("AGENT_CRAWLER_KEY", "xnai-crawler-secret-2026"): {
        "user": "crawler",
        "email": "crawler@xoe-novai.local",
        "groups": "agents"
    }
}

@app.get("/verify")
async def verify(request: Request, x_api_key: str = Header(None)):
    """
    Verification endpoint for Caddy forward_auth.
    Returns 200 if authorized, 401 otherwise.
    """
    if not x_api_key or x_api_key not in INTERNAL_AGENTS:
        raise HTTPException(status_code=401, detail="Unauthorized Agent")
    
    agent = INTERNAL_AGENTS[x_api_key]
    
    # Caddy will copy these headers to the backend request
    response = Response(status_code=200)
    response.headers["Remote-User"] = agent["user"]
    response.headers["Remote-Email"] = agent["email"]
    response.headers["Remote-Groups"] = agent["groups"]
    
    return response

@app.get("/health")
async def health():
    return {"status": "healthy"}
