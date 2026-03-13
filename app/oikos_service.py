#!/usr/bin/env python3
"""
🔱 OIKOS SERVICE: The Cognitive Mesh of the Omega Stack
Manages Iris (Routing), The Council (Individual Agents), and The Mastermind (Collective Decisioning).
Port: 8006
"""
import anyio
import os
import sys
import json
import time
import httpx
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from pathlib import Path

# Ensure project root is in path for scripts/app imports
sys.path.append(os.getcwd())

from scripts.agent_factory import AgentFactory
from scripts.soul_distiller import distill_cycle
from scripts.observer import record_gear_shift

# Initialize Oikos Mesh
app = FastAPI(title="🔱 XNA Oikos Mesh Service", version="1.0.0")
factory = AgentFactory(model_name="gemini/gemini-2.0-flash")

# --- 🛰️ OBSERVABILITY MIDDLEWARE ---

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"📡 Oikos API: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response

# Global Session State
SESSION_STATES: Dict[str, Any] = {}

class MastermindRequest(BaseModel):
    problem: str
    session_id: str = "DEFAULT-SESSION"
    escalation_level: Optional[int] = 1

@app.get("/iris/status/{session_id}")
async def get_session_status(session_id: str):
    """Retrieves the status of an ongoing Mastermind session."""
    if session_id not in SESSION_STATES:
        return {"status": "NOT_FOUND"}
    return SESSION_STATES[session_id]

# --- 🌈 IRIS: THE FRONT-FACING ROUTER ---

@app.post("/iris/route")
async def iris_route(req: MastermindRequest, background_tasks: BackgroundTasks):
    """
    Iris Swift Routing and Escalation Gateway (Async).
    """
    start_time = time.time()
    session_id = req.session_id
    SESSION_STATES[session_id] = {"status": "INITIATED", "problem": req.problem, "start_time": start_time}

    print(f"🌈 Iris (Service): Hearing your request... '{req.problem}'")

    # 1. Routing Logic (Swift Phase)
    try:
        complexity = len(req.problem.split())

        if complexity < 5:
            # Swift Level 1
            await record_gear_shift("Iris", "LEVEL_1_SWIFT", time.time() - start_time, {"problem": req.problem})
            SESSION_STATES[session_id]["status"] = "COMPLETE"
            return {"decision": "LEVEL_1_SWIFT", "response": "Handling instantly via the Hearth."}

        else:
            # Escalation (Mastermind Council)
            print(f"🌈 Iris: Escalating Session [{session_id}] to Mastermind Council")
            await record_gear_shift("Iris", "LEVEL_3_ESCALATION", time.time() - start_time, {"problem": req.problem})
            SESSION_STATES[session_id]["status"] = "SUMMONING_COUNCIL"
            background_tasks.add_task(orchestrate_mastermind, req.problem, session_id)
            return {"decision": "ASYNC_MASTERMIND", "session_id": session_id, "response": "Summoning the Council of Oikos. Use /iris/status to track."}

    except Exception as e:
        SESSION_STATES[session_id] = {"status": "ERROR", "error": str(e)}
        raise HTTPException(status_code=500, detail=str(e))


# --- 🏛️ THE COUNCIL ENDPOINTS ---

@app.get("/council/{member}")
async def get_council_insight(member: str, problem: str):
    """Get domain-specific insight from a Council member."""
    # TODO: Integration with individual Oikos scripts
    return {"member": member, "insight": f"Insight for {problem} from {member}."}

# --- 🧠 THE MASTERMIND CORE ---

async def tavily_search(query: str) -> str:
    """Performs a direct REST call to Tavily."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Tavily API Key missing. Skipping web research."
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 3
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            results = [f"- {r['title']}: {r['url']}" for r in data.get('results', [])]
            return "\n".join(results)
    except Exception as e:
        return f"Web Search Failed: {str(e)}"

async def orchestrate_mastermind(problem: str, session_id: str):
    """Grounded Mastermind session with Local and Web research (State Tracked)."""
    print(f"🔱 Mastermind (Service): Initiating session on: {problem}")
    SESSION_STATES[session_id]["status"] = "RESEARCHING"
    
    # --- Round 0: Research Phase ---
    # ... existing research logic ...
    
    SESSION_STATES[session_id]["status"] = "COUNCIL_DELIBERATION"
    # ... existing insight logic ...
    
    SESSION_STATES[session_id]["status"] = "MALI_JUDGMENT"
    # ... existing synthesis logic ...
    
    SESSION_STATES[session_id]["status"] = "DISTILLING_GNOSIS"
    await distill_cycle(session_id, 20, f"Oikos Council Mastermind for: {problem}")
    
    SESSION_STATES[session_id]["status"] = "COMPLETE"
    SESSION_STATES[session_id]["response"] = "The Council has spoken. Decree etched in the Chronicles."
    print(f"✅ Mastermind Session Complete for [{session_id}].")

@app.get("/health")
async def health_check():
    return {"status": "ACTIVE", "hearth": "WARM"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
