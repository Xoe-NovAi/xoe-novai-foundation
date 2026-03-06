import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.XNAi_rag_app.core.oauth_manager import OAuthManager

async def main():
    m = OAuthManager()
    creds = await m.get_credentials('gemini_oauth_01')
    print(f"CREDS: {creds}")
    valid = await m.is_valid('gemini_oauth_01')
    print(f"VALID: {valid}")

if __name__ == "__main__":
    asyncio.run(main())
