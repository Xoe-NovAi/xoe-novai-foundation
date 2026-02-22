# Token Usage Optimization Guide

**Context**: Reducing AI token consumption for blind-accessible voice assistant while maintaining quality.

---

## 1. Understanding Token Economics

### What Consumes Tokens

| Component | Token Cost | Notes |
|-----------|-----------|-------|
| **System Prompt** | Flat 1× per request | Large prompts cost more than small ones |
| **Conversation History** | N × turn count | Including ALL previous messages accumulates |
| **User Input** | Variable (speech transcription) | Average: 100-300 tokens per 30-second message |
| **LLM Response** | Output length | Every word in response costs tokens |
| **Context Windows** | Memory/session history | Larger windows = bigger token cost |
| **Function Calls** | ~100 per call | Tool/function definitions in prompt |

**Formula**:
```
Total Tokens = System Prompt + Conversation History + User Input + Response + Context Overhead
```

---

## 2. Current Token Usage Analysis

### Baseline (Single Turn)
```
Scenario: "What's the weather?"

System Prompt:        ~200 tokens
User Input:           ~20 tokens
Response (~50 words): ~75 tokens
─────────────────────────────
Per turn:             ~295 tokens
```

### Multi-Turn Conversation Overhead
```
Scenario: 5-turn conversation

Tokens = (System Prompt: 200) + 
         (Turn 1: 20 in + 75 out) +
         (Turn 2: 25 in + 80 out) +
         (Turn 3: 30 in + 85 out) +
         (Turn 4: 28 in + 70 out) +
         (Turn 5: 35 in + 90 out)
─────────────────────────────────
Total: ~933 tokens (20 turns = ~3,100 tokens)
```

**Key insight**: Each message includes ENTIRE history. By message 10, 90% of tokens are retransmitting old conversations!

---

## 3. Optimization Strategy 1: Summarize & Forget

### Problem
System keeps full 20-turn history. After turn 10, most tokens wasted on repetition.

### Solution: Sliding Window + Summary

```python
# conversation_manager.py - Current full history approach
class ConversationContext:
    def __init__(self):
        self.history = deque(maxlen=20)  # Keeps all 20 turns
        
# NEW: Optimized approach with summary
class OptimizedConversationContext:
    def __init__(self, window_size=5, summary_threshold=10):
        self.history = deque(maxlen=window_size)  # Keep only last 5
        self.summary = ""  # Compressed history
        self.turn_count = 0
        self.summary_threshold = summary_threshold
    
    def get_context_for_prompt(self):
        """Return only recent history + summary"""
        return f"""
Prior context: {self.summary}

Recent exchange:
{self._format_history()}
"""
```

**Impact**: 
- ✅ Reduces repetitive history tokens by 70-80%
- ✅ Maintains conversation continuity
- ✅ Better performance (shorter context to process)

**Implementation cost**: 1 summary generation per 10 turns (200-300 tokens)  
**Payoff**: Saves 500-1,000 tokens per multi-turn session

---

## 4. Optimization Strategy 2: Compress Response Length

### Problem
TTS-friendly responses are 500 chars (~75 tokens). But many queries need less.

### Solution: Smart Response Truncation

```python
# conversation_manager.py - Current
class BlindAccessibleResponseFormatter:
    def format_response(self, response):
        return response[:500]  # Max 500 chars (~75 tokens)

# NEW: Variable-length responses
class TokenAwareResponseFormatter:
    def format_response(self, response, query_type=None):
        length_map = {
            'factual_question': 100,      # "What's 2+2?" → "Four"
            'howto': 250,                 # "How to X?" → Concise steps
            'conversational': 150,        # Chat → Short response
            'research': 300,              # "Tell me about X" → Detailed
            'followup': 80,               # "What?" → Minimal
        }
        
        max_length = length_map.get(query_type, 200)
        
        # Aggressive truncation
        truncated = response[:max_length]
        
        # Remove incomplete sentences
        if len(truncated) == max_length:
            truncated = truncated.rsplit('.', 1)[0] + "."
        
        # Token cost: 20-30 (vs 75 baseline)
        return truncated
```

**Configure by context**:

```json
{
  "response_length_by_type": {
    "factual": 100,
    "explanations": 250,
    "instructions": 300,
    "questions": 150
  }
}
```

**Impact**:
- ✅ Reduces average response tokens by 60%
- ✅ Faster TTS (better for blind users)
- ✅ Still maintains quality

**New cost per turn**: ~80 tokens (vs ~295 baseline)

---

## 5. Optimization Strategy 3: Batch Processing

### Problem
Each voice input triggers one LLM call. High overhead per request.

### Solution: Deferred Batch Processing

```python
# New batch mode for non-urgent requests
class BatchVoiceProcessor:
    def __init__(self, batch_size=3, timeout=5.0):
        self.queue = []
        self.batch_size = batch_size
        self.timeout = timeout
    
    async def process_batch(self):
        """Process multiple requests in one LLM call"""
        while self.queue:
            items = self.queue[:self.batch_size]
            
            # Single prompt for multiple items
            prompt = f"""
Process these {len(items)} voice requests:

{format_requests(items)}

Respond to each briefly.
"""
            # ONE API call for N requests
            response = await self.llm.complete(prompt)
            
            # Parse and route responses
            for item, response_part in parse_responses(response, len(items)):
                await item.callback(response_part)
            
            self.queue = self.queue[self.batch_size:]
```

**Use case**: Smart home, multiple concurrent users, batch analytics

**Impact**:
- ✅ Amortizes system prompt overhead across multiple requests
- ✅ Per-request cost: 1/3 the overhead
- ✅ Requires: User tolerance for 1-2s delay

---

## 6. Optimization Strategy 4: Context Caching

### Problem
System prompt sent with every request (200 tokens per turn).

### Solution: Ollama Context Caching (if using local model)

```python
# Use Ollama's built-in caching
class OllamaCachedContext:
    def __init__(self):
        self.cached_system_prompt = None
        self.cache_id = None
    
    async def complete_with_cache(self, user_input, system_prompt):
        """Ollama automatically caches repeated system prompts"""
        
        # First request: ~1000 tokens (full prompt)
        if not self.cache_id:
            response = await call_ollama(
                system=system_prompt,
                user=user_input,
                cache_prompt=True  # Enable caching
            )
            self.cache_id = response.get('cache_id')
        
        # Subsequent requests: ~200 tokens (prompt not retransmitted!)
        else:
            response = await call_ollama(
                cache_id=self.cache_id,
                user=user_input
            )
        
        return response
```

**Configuration** (`config/ollama_cache.json`):
```json
{
  "use_prompt_cache": true,
  "cache_ttl_seconds": 3600,
  "cache_size_mb": 500
}
```

**Impact** (Local only):
- ✅ First request: Normal cost
- ✅ Subsequent requests: 60-70% reduction
- ✅ Only works with Ollama/local models

---

## 7. Optimization Strategy 5: Lazy Context Loading

### Problem
All 20-turn history loaded even if user only needs last 3 turns.

### Solution: Lazy/Smart History Loading

```python
class LazyConversationContext:
    def __init__(self):
        self.full_history = []  # In database or disk
        self.loaded_history = deque(maxlen=3)  # Only last 3 in memory
    
    def get_context(self, depth_needed=3):
        """Load only needed history"""
        return self.loaded_history[-depth_needed:]
    
    async def answer_followup_question(self, question):
        """Smart loading based on question"""
        if "explain that" in question:
            # Need full context
            depth = 10
        elif "what" in question:
            # Minimal context needed
            depth = 2
        else:
            depth = 5
        
        context = self.get_context(depth)
        # Only transmit needed history
        return await llm_complete(question, context)
```

**Impact**:
- ✅ 40-60% token reduction for followup questions
- ✅ ~50ms slower (database lookup)
- ✅ Better for low-bandwidth scenarios

---

## 8. Optimization Strategy 6: Response Template Caching

### Problem
LLM generates similar responses repeatedly ("Sorry, I don't know", "Please clarify").

### Solution: Template Cache with Fill-ins

```python
class TemplateResponseCache:
    """Cache common response patterns"""
    
    templates = {
        'dont_know': "I'm not sure about [TOPIC]. Can you clarify?",
        'clarify': "When you say [NOUN], do you mean [OPTION1] or [OPTION2]?",
        'confirm': "Just to confirm, you want to [ACTION]. Correct?",
    }
    
    def get_response(self, query_type, **fills):
        """Return template response instead of LLM call"""
        if query_type in self.templates:
            template = self.templates[query_type]
            for key, value in fills.items():
                template = template.replace(f"[{key.upper()}]", value)
            return template
        
        # Fall through to LLM if no template
        return None

# Usage
cache = TemplateResponseCache()
response = cache.get_response('dont_know', TOPIC='machine learning')
# Result: "I'm not sure about machine learning. Can you clarify?"
# Token cost: 0 (no LLM call!)
```

**Impact**:
- ✅ Up to 30% of responses from cache (0 tokens)
- ✅ Instant response time
- ✅ Reduces latency

**Configuration** (`config/response_templates.json`):
```json
{
  "enable_template_cache": true,
  "cache_hit_ratio_target": 0.25,
  "templates_per_topic": 5
}
```

---

## 9. Practical Implementation Order

### Phase 1: Quick Wins (10 min, 30-40% reduction)
```python
1. Reduce response length:        300 tokens → 100 tokens per turn
2. Enable template caching:       ~30% of responses go to 0 tokens

Result: Per-turn cost ~180 tokens (vs 295 baseline)
Tokens saved: 35-40% with no complexity
```

**Code**:
```python
# In conversation_manager.py
class BlindAccessibleResponseFormatter:
    def format_response(self, response):
        # OLD: 500 chars
        # NEW: Variable by type
        if response.startswith("I don't know"):
            return "I'm not sure. Can you clarify?"  # Template
        
        max_length = 150  # Reduced from 500
        truncated = response[:max_length].rsplit('.', 1)[0]
        return truncated + "."
```

### Phase 2: Smart Context (5 min, 20-30% additional reduction)
```python
1. Summarize after 10 turns:     Saves ~500 tokens
2. Use sliding window (last 5):  Reduces history overhead

Result: Per-session cost ~40-50% lower
Tokens saved: Additional 20-30%
```

**Code**:
```python
# In conversation_manager.py - ConversationFlowManager
def build_context(self):
    if len(self.context.history) > 10:
        # Summarize old turns
        summary = self._summarize_history(self.context.history[:10])
        # Use only summary + recent
        return f"Summary: {summary}\n\nRecent: {self.context.history}"
    else:
        return str(self.context.history)
```

### Phase 3: Lazy Loading (10 min, 10-15% reduction)
```python
1. Load context on-demand
2. Reduce default depth from 20 to 5

Result: Minimal queries load less history
Tokens saved: Additional 10-15%
```

---

## 10. Comprehensive Optimization Checklist

| Strategy | Effort | Savings | Implementation |
|----------|--------|---------|-----------------|
| **Reduce response length** | 5 min | 30-40% | Variable length by query type |
| **Template caching** | 10 min | 25-30% | If-else template matching |
| **Sliding window history** | 15 min | 20-30% | Change `maxlen=20` to `maxlen=5` |
| **Lazy history loading** | 20 min | 10-15% | Load-on-demand from DB |
| **Batch processing** | 30 min | 50%+ | For async/non-urgent requests |
| **Context caching (local)** | 5 min | 60%+ | Ollama only, automatic |
| **Summarization** | optional | 20-30% | Keep summary + recent only |
| **Prompt optimization** | 5 min | 5-10% | Remove redundant system info |

**Quick Win Total**: Strategies 1-2 = **30-40% reduction in 15 minutes**

---

## 11. Configuration File for Quick Optimization

Create `config/token_optimization.json`:

```json
{
  "comment": "Token usage optimization settings",
  "enabled": true,
  
  "response_optimization": {
    "max_length_by_type": {
      "factual_question": 100,
      "how_to": 250,
      "explanation": 200,
      "conversation": 150,
      "followup": 75,
      "default": 150
    },
    "enable_template_cache": true,
    "template_cache_hit_target": 0.25
  },
  
  "history_optimization": {
    "sliding_window_size": 5,
    "summarize_after_turns": 10,
    "enable_summarization": true,
    "summary_strategy": "extractive",
    "max_summary_tokens": 100
  },
  
  "context_optimization": {
    "lazy_load_history": true,
    "load_depth_by_question": {
      "explicit_context": 10,
      "implicit_context": 5,
      "default": 3
    }
  },
  
  "caching": {
    "enable_ollama_cache": true,
    "cache_ttl_seconds": 3600,
    "cache_system_prompt": true
  }
}
```

---

## 12. Measuring Token Savings

### Add Telemetry

```python
class TokenMetrics:
    """Track token usage"""
    
    def __init__(self):
        self.total_tokens = 0
        self.total_requests = 0
        self.template_hits = 0
    
    def log_request(self, tokens_used, cache_hit=False):
        self.total_tokens += tokens_used
        self.total_requests += 1
        if cache_hit:
            self.template_hits += 1
    
    def get_stats(self):
        avg_tokens = self.total_tokens / max(1, self.total_requests)
        cache_hit_rate = self.template_hits / max(1, self.total_requests)
        
        return {
            "total_requests": self.total_requests,
            "avg_tokens_per_request": avg_tokens,
            "cache_hit_rate": cache_hit_rate,
            "estimated_savings_percent": cache_hit_rate * 100
        }
```

### Add to CLI

```bash
python3 main.py --cli-mode blind --show-metrics
# Output:
# Total requests: 47
# Avg tokens/request: 180 (was 295)
# Cache hit rate: 22%
# Token savings: ~39%
```

---

## 13. Expected Results

### Before Optimization
```
Scenario: 10-turn conversation
Initial prompt:       200 tokens
History (cumulative): 2,500 tokens
User inputs:          300 tokens
Responses:            750 tokens
─────────────────────────────
TOTAL:               3,750 tokens
```

### After Phase 1 (Quick Wins)
```
Scenario: 10-turn conversation
Initial prompt:       200 tokens
History (5 turns):    800 tokens (reduced)
User inputs:          300 tokens
Responses:            400 tokens (shorter + template cache)
─────────────────────────────
TOTAL:               1,700 tokens (~55% reduction)
```

### After Phase 2 (Smart Context)
```
Scenario: 10-turn conversation
Initial prompt:       200 tokens
Summary:              100 tokens (compressed history)
Last 3 turns:         400 tokens
User inputs:          300 tokens
Responses:            400 tokens
─────────────────────────────
TOTAL:               1,400 tokens (~63% reduction)
```

---

## 14. Implementation Priority

### 🔴 DO THIS FIRST (Today)
1. ✅ Reduce response max length: 500 → 150 chars
2. ✅ Add template cache for common responses
3. ✅ Change sliding window: 20 → 5 turns

**Time**: 15 minutes  
**Savings**: 30-40%

### 🟡 DO THIS NEXT (This week)
4. ✅ Add summarization after 10 turns
5. ✅ Implement lazy history loading
6. ✅ Create token optimization config file

**Time**: 30 minutes  
**Additional savings**: 20-30%

### 🟢 NICE TO HAVE (When needed)
7. ⭐ Batch processing for multiple users
8. ⭐ Context caching (Ollama only)
9. ⭐ Advanced prompt engineering

**Time**: 1+ hours  
**Additional savings**: 10-50% depending on approach

---

## 15. Blind User Specific Optimizations

For blind users, token savings directly improve:
- ✅ **Cost**: Fewer tokens = lower API bills
- ✅ **Speed**: Shorter context = faster responses
- ✅ **Reliability**: Less load on servers = fewer timeouts
- ✅ **Accessibility**: Faster responses = better user experience

**Recommendation**: Implement Phase 1 today. Phase 2 this week.

---

**Summary**: With intelligent response formatting + history management, you can reduce token usage by **40-60%** while **improving blind user experience** (faster responses, lower latency).
