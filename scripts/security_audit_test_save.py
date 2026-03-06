
import asyncio
import os
from pathlib import Path
from app.XNAi_rag_app.core.oauth_manager import OAuthManager

async def test_oauth_wiping_on_save():
    print("Testing OAuthManager wiping-on-save risk...")
    storage = Path("./test_oauth_save.json")
    if storage.exists(): storage.unlink()
    
    # 1. Setup credentials
    mgr = OAuthManager(storage_path=str(storage))
    await mgr.save_credentials("acc1", {"token": "secret1"})
    print("Saved acc1")
    
    # 2. New instance, call save without load
    mgr2 = OAuthManager(storage_path=str(storage))
    # At this point mgr2.credentials is {}
    await mgr2.save_credentials("acc2", {"token": "secret2"})
    print("Saved acc2 (without loading acc1 first)")
    
    # 3. Check if acc1 is still there
    await mgr2.load_credentials()
    if "acc1" not in mgr2.credentials:
        print("❌ CRITICAL: OAuth storage for acc1 was WIPED by save_credentials('acc2') call!")
    else:
        print("✅ OAuth storage preserved (This shouldn't happen with current code!)")

if __name__ == "__main__":
    asyncio.run(test_oauth_wiping_on_save())
