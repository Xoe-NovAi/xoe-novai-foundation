# Fix for OpenCode 263 Questions Issue

## Problem Analysis

**Error Message:**
```
Error: The question tool was called with invalid arguments: [
  {
    "expected": "array",
    "code": "invalid_type",
    "path": ["questions"],
    "message": "Invalid input: expected array, received string"
  }
]
```

**Root Cause:**
The OpenCode MCP client is calling the question tool with a string instead of an array, causing it to loop 263 times asking the same question before reading files.

## Solution

### 1. Fix MCP Client Question Tool Calls

The MCP client needs to be updated to pass questions as an array instead of a string.

### 2. Update Memory Bank MCP Server

The memory bank MCP server should handle both single questions and arrays gracefully.

## Implementation

### Fix 1: Update MCP Client

```python
# Before (incorrect - causes 263 loops):
await mcp_client.call_tool("ask_question", {
    "questions": "load memory-bank"
})

# After (correct):
await mcp_client.call_tool("ask_question", {
    "questions": ["load memory-bank"]
})
```

### Fix 2: Update Memory Bank MCP Server

```python
# In the memory bank MCP server, update the question tool handler:
async def handle_question_tool(self, questions: Union[str, List[str]], **kwargs):
    """Handle question tool with both string and array inputs."""
    if isinstance(questions, str):
        questions = [questions]
    
    # Process the array of questions
    results = []
    for question in questions:
        result = await self.process_single_question(question, **kwargs)
        results.append(result)
    
    return results
```

## Files to Update

1. **MCP Client Implementation** - Where the question tool is called
2. **Memory Bank MCP Server** - To handle both formats gracefully

## Testing

After implementing the fix:

1. Test with single question: `["load memory-bank"]`
2. Test with multiple questions: `["load memory-bank", "analyze context"]`
3. Verify no more "expected array, received string" errors
4. Confirm the 263-question loop is eliminated

## Prevention

Add input validation in the MCP client to ensure questions are always passed as arrays.

## Expected Results

- **Before:** 263 questions asked before reading files
- **After:** 1 question asked, then files are read immediately

This fix should resolve the immediate issue you're experiencing with SambaNova/OpenCode.