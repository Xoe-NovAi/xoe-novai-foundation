# EKB Gem: FastAPI Rate Limiter (SlowAPI) Stability

## Issue
FastAPI service (RAG API) crash-loops with `Exception: No "request" or "websocket" argument on function` when using `@limiter.limit`.

## Root Cause
The `slowapi` library requires the first or second argument of the decorated route function to be an instance of `fastapi.Request`. If missing, the rate limiter cannot identify the client IP or session, causing an initialization exception during the FastAPI startup sequence.

## Remediation
Ensure all functions decorated with `@limiter.limit` include `request: Request` in their signature, even if the request object is not explicitly used within the function body.

```python
# Before (Causes Crash)
@app.post("/auth/login")
@limiter.limit("30/minute")
async def login(login_req: LoginRequest):
    ...

# After (Stable)
@app.post("/auth/login")
@limiter.limit("30/minute")
async def login(request: Request, login_req: LoginRequest):
    ...
```

## Prevention
1. **Linter/Static Analysis**: Use type checking to ensure `Request` is present in limited routes.
2. **Template Standard**: All Xoe-NovAi API templates must include `request: Request` by default for all endpoints to allow for future rate limiting without refactoring.
