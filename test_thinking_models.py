#!/usr/bin/env python3
"""
Test Script: Thinking Model Performance Measurement

Measures:
1. Latency (time to response)
2. Token consumption
3. Quality (subjective)
4. Thinking vs regular model comparison
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

class ThinkingModelTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
    
    def run_opencode_chat(self, model: str, prompt: str, timeout: int = 60) -> Optional[Dict]:
        """
        Run OpenCode chat command and capture output
        
        Returns: Dict with response, tokens, latency
        """
        try:
            start_time = time.time()
            
            # Run opencode chat command
            cmd = [
                "opencode", "chat",
                "--model", model,
                "--timeout", str(timeout),
                prompt
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            latency = time.time() - start_time
            
            if result.returncode != 0:
                print(f"❌ Error running {model}: {result.stderr[:200]}")
                return None
            
            output = result.stdout.strip()
            
            # Try to extract token info if available
            # Format varies by OpenCode version
            token_info = self._parse_token_info(output)
            
            return {
                "model": model,
                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                "response": output[:200] + "..." if len(output) > 200 else output,
                "latency_seconds": latency,
                "tokens": token_info,
                "success": True
            }
        
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout for {model}")
            return {
                "model": model,
                "error": "timeout",
                "success": False
            }
        except Exception as e:
            print(f"❌ Exception testing {model}: {e}")
            return {
                "model": model,
                "error": str(e),
                "success": False
            }
    
    def _parse_token_info(self, output: str) -> Optional[Dict]:
        """Try to extract token info from OpenCode output"""
        # Look for patterns like "tokens: 1234" or "tokens used: 1234"
        token_patterns = [
            r"tokens[:\s]+(\d+)",
            r"input[:\s]+(\d+).*output[:\s]+(\d+)",
        ]
        
        for pattern in token_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    return {"total": int(match.group(1))}
                else:
                    return {
                        "input": int(match.group(1)),
                        "output": int(match.group(2))
                    }
        return None
    
    def test_model_pair(self, thinking_model: str, regular_model: str, 
                       prompt: str, label: str) -> Dict:
        """Test a thinking model vs regular model on same prompt"""
        print(f"\n{'='*70}")
        print(f"Test: {label}")
        print(f"Prompt: {prompt[:60]}...")
        print('='*70)
        
        results = {}
        
        # Test thinking model
        print(f"🧠 Testing thinking model: {thinking_model}")
        thinking_result = self.run_opencode_chat(thinking_model, prompt)
        if thinking_result:
            results["thinking"] = thinking_result
            print(f"   ✅ Latency: {thinking_result['latency_seconds']:.2f}s")
            if thinking_result.get("tokens"):
                print(f"   Tokens: {thinking_result['tokens']}")
        
        # Test regular model
        print(f"\n⚡ Testing regular model: {regular_model}")
        regular_result = self.run_opencode_chat(regular_model, prompt)
        if regular_result:
            results["regular"] = regular_result
            print(f"   ✅ Latency: {regular_result['latency_seconds']:.2f}s")
            if regular_result.get("tokens"):
                print(f"   Tokens: {regular_result['tokens']}")
        
        # Calculate comparison
        if "thinking" in results and "regular" in results:
            t = results["thinking"]["latency_seconds"]
            r = results["regular"]["latency_seconds"]
            speedup = (t - r) / r * 100 if r > 0 else 0
            results["comparison"] = {
                "latency_overhead_percent": speedup,
                "thinking_slower": speedup > 0,
                "speedup_factor": t / r if r > 0 else None
            }
            print(f"\n📊 Comparison:")
            print(f"   Thinking latency: {t:.2f}s")
            print(f"   Regular latency:  {r:.2f}s")
            print(f"   Overhead: {speedup:+.1f}%")
        
        return results
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n🚀 THINKING MODEL PERFORMANCE TEST SUITE")
        print("="*70)
        
        # Define test cases
        test_cases = [
            {
                "label": "1. SIMPLE TASK: Code explanation",
                "prompt": "Explain what this Python function does in 1 sentence: def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
                "thinking_model": "google/antigravity-claude-opus-4-6-thinking",
                "regular_model": "google/antigravity-claude-opus-4-6"
            },
            {
                "label": "2. MEDIUM TASK: Architecture decision",
                "prompt": "Should we use microservices or monolith for a SaaS app handling 1M daily users? Consider scalability, cost, and complexity. Give 2-3 key reasons.",
                "thinking_model": "google/antigravity-claude-opus-4-6-thinking",
                "regular_model": "google/antigravity-claude-opus-4-6"
            },
            {
                "label": "3. COMPLEX TASK: Multi-step problem solving",
                "prompt": "Design a system to detect duplicate items in large datasets with 99% accuracy, <100ms latency, <1GB memory. Describe algorithm, data structures, and tradeoffs.",
                "thinking_model": "google/antigravity-claude-opus-4-6-thinking",
                "regular_model": "google/antigravity-claude-opus-4-6"
            },
        ]
        
        # Run tests
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = self.test_model_pair(
                    thinking_model=test_case["thinking_model"],
                    regular_model=test_case["regular_model"],
                    prompt=test_case["prompt"],
                    label=test_case["label"]
                )
                self.results["tests"].append({
                    "test_number": i,
                    "label": test_case["label"],
                    "results": result
                })
            except KeyboardInterrupt:
                print("\n⚠️ Test interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Test {i} failed: {e}")
                continue
        
        # Generate summary
        self._generate_summary()
        
        # Save results
        self._save_results()
    
    def _generate_summary(self):
        """Generate summary statistics"""
        thinking_latencies = []
        regular_latencies = []
        
        for test in self.results["tests"]:
            if "comparison" in test.get("results", {}):
                if "thinking" in test["results"]:
                    thinking_latencies.append(test["results"]["thinking"]["latency_seconds"])
                if "regular" in test["results"]:
                    regular_latencies.append(test["results"]["regular"]["latency_seconds"])
        
        if thinking_latencies and regular_latencies:
            avg_thinking = sum(thinking_latencies) / len(thinking_latencies)
            avg_regular = sum(regular_latencies) / len(regular_latencies)
            overhead = ((avg_thinking - avg_regular) / avg_regular * 100) if avg_regular > 0 else 0
            
            self.results["summary"] = {
                "tests_completed": len(self.results["tests"]),
                "average_thinking_latency": avg_thinking,
                "average_regular_latency": avg_regular,
                "average_overhead_percent": overhead,
                "conclusion": self._generate_conclusion(overhead)
            }
    
    def _generate_conclusion(self, overhead: float) -> str:
        """Generate conclusion based on overhead"""
        if overhead > 30:
            return "Thinking models significantly slower (>30%). Use for background tasks only."
        elif overhead > 15:
            return "Thinking models moderately slower (15-30%). Use strategically for complex reasoning."
        elif overhead < 0:
            return "Thinking models faster (unexpected!). Verify measurements."
        else:
            return "Thinking models slightly slower (<15%). Good for reasoning tasks with flexible SLA."
    
    def _save_results(self):
        """Save results to JSON file"""
        filename = f"thinking_model_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n✅ Results saved to {filename}")
            return filename
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
            return None

def main():
    print("🧠 THINKING MODEL PERFORMANCE TEST")
    print("=" * 70)
    print("This test will measure latency and performance of thinking models")
    print("compared to regular models.")
    print("\nRequirements:")
    print("  - OpenCode installed and configured")
    print("  - Antigravity models available (google/antigravity-*)")
    print("  - Network connectivity")
    print("\nNote: This may use quota. Monitor your account if needed.")
    print("=" * 70)
    
    response = input("\nProceed with testing? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    tester = ThinkingModelTester()
    tester.run_all_tests()
    
    # Print summary
    if tester.results["summary"]:
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        summary = tester.results["summary"]
        print(f"Tests completed: {summary['tests_completed']}")
        print(f"Average thinking latency: {summary['average_thinking_latency']:.2f}s")
        print(f"Average regular latency:  {summary['average_regular_latency']:.2f}s")
        print(f"Average overhead: {summary['average_overhead_percent']:+.1f}%")
        print(f"\nConclusion: {summary['conclusion']}")
        print("="*70)

if __name__ == "__main__":
    main()
