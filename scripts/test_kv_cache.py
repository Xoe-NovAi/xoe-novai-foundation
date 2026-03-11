import time
import psutil
import os
from llama_cpp import Llama

def monitor_ram(n_ctx, type_k, type_v):
    print(f"🚀 Testing n_ctx={n_ctx}, type_k={type_k}, type_v={type_v}")
    
    process = psutil.Process(os.getpid())
    base_mem = process.memory_info().rss / 1024 / 1024
    print(f"  Base RAM: {base_mem:.2f} MB")
    
    try:
        llm = Llama(
            model_path="/models/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
            n_ctx=n_ctx,
            type_k=type_k,
            type_v=type_v,
            n_threads=6,
            verbose=False
        )
        
        load_mem = process.memory_info().rss / 1024 / 1024
        print(f"  RAM after Load: {load_mem:.2f} MB (Delta: {load_mem - base_mem:.2f} MB)")
        
        # Fill context
        prompt = "User: Say hello " + "x" * (n_ctx - 100) + "\nAssistant:"
        llm(prompt, max_tokens=1)
        
        final_mem = process.memory_info().rss / 1024 / 1024
        print(f"  RAM after Fill: {final_mem:.2f} MB (Delta from Load: {final_mem - load_mem:.2f} MB)")
        
        return final_mem
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

if __name__ == "__main__":
    # Test Baseline (F16)
    monitor_ram(2048, 0, 0) # GGML_TYPE_F16 = 0
    
    # Test Q4_0 (GGML_TYPE_Q4_0 = 2)
    # Note: enum values might vary, better use string names if supported by wrapper
    # but llama-cpp-python often exposes them as ints. 
    # Q4_0 = 2, Q8_0 = 8
    monitor_ram(8192, 2, 2)
    monitor_ram(32768, 2, 2)
