
import asyncio
import os
import shutil
from pathlib import Path
from app.XNAi_rag_app.core.oauth_manager import OAuthManager
from app.XNAi_rag_app.core.paths import resolve_path

async def test_oauth_wiping():
    print("Testing OAuthManager wiping risk...")
    storage = Path("./test_oauth.json")
    key_path = Path("./.oauth_key")
    if storage.exists(): storage.unlink()
    if key_path.exists(): key_path.unlink()
    
    # 1. Setup credentials
    mgr = OAuthManager(storage_path=str(storage))
    # Hack to use local key path for test
    mgr.encryption_key = mgr._get_or_create_encryption_key()
    # We need to manually move the key for this test because _get_or_create_encryption_key uses storage_path.parent
    
    await mgr.save_credentials("acc1", {"token": "secret"})
    print("Saved acc1")
    
    # 2. New instance, call delete without load
    mgr2 = OAuthManager(storage_path=str(storage))
    # At this point mgr2.credentials is {}
    await mgr2.delete_credentials("nonexistent")
    
    # Check if storage still has acc1
    await mgr2.load_credentials()
    if "acc1" not in mgr2.credentials:
        print("❌ CRITICAL: OAuth storage was WIPED by delete_credentials call!")
    else:
        print("✅ OAuth storage preserved (because 'nonexistent' wasn't found in empty {})")
        
    # 3. What if we delete 'acc1' without loading?
    mgr3 = OAuthManager(storage_path=str(storage))
    await mgr3.delete_credentials("acc1")
    await mgr3.load_credentials()
    if "acc1" not in mgr3.credentials:
         # This is expected if it worked, but did it preserve others?
         pass

def test_path_leakage():
    print("\nTesting path variable leakage...")
    os.environ["SECRET_VAR"] = "SUPER_SECRET_VALUE"
    path = resolve_path("${SECRET_VAR}/some/file")
    print(f"Resolved path: {path}")
    if "SUPER_SECRET_VALUE" in str(path):
        print("❌ RISK: resolve_path leaks environment variables via expandvars")
    else:
        print("✅ resolve_path does not leak environment variables (Wait, it should if it uses expandvars)")

if __name__ == "__main__":
    asyncio.run(test_oauth_wiping())
    test_path_leakage()
