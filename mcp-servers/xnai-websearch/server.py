import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

mcp = FastMCP("XNAi-WebSearch")

@mcp.tool()
async def web_search(query: str, provider: str = "duckduckgo"):
    """🔱 Archon Mandate: Perform a web search (Tavily/Serper or fallback to DuckDuckGo)."""
    
    if provider == "tavily":
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Error: TAVILY_API_KEY not found. Falling back to DuckDuckGo."
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": api_key, "query": query, "search_depth": "basic"}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return f"Tavily search failed: {e}"

    if provider == "serper":
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY not found. Falling back to DuckDuckGo."
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                    json={"q": query}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return f"Serper search failed: {e}"

    # Default: DuckDuckGo (Placeholder implementation or via library)
    # Using a simple duckduckgo-search wrapper if available or just returning a note
    return {
        "query": query,
        "results": [
            {
                "title": "DuckDuckGo Search Placeholder",
                "link": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                "snippet": "DuckDuckGo search results would appear here in a fully integrated environment."
            }
        ],
        "note": "🔱 Archon: Please provide TAVILY_API_KEY or SERPER_API_KEY for deep research integration."
    }

if __name__ == "__main__":
    mcp.run()
