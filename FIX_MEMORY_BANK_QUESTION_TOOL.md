# Fix for SambaNova Memory Bank Question Tool Issue

## Problem Analysis

The error message indicates:
```
The question tool was called with invalid arguments: [
  {
    "expected": "array",
    "code": "invalid_type",
    "path": ["questions"],
    "message": "Invalid input: expected array, received string"
  }
]
```

This means the MCP client is calling a question tool with a string value for the `questions` parameter, but the tool expects an array.

## Root Cause

The issue is in the MCP client implementation where it's passing a single question string instead of an array of questions to the memory bank tool.

## Solution

### 1. Fix the MCP Client Question Tool Usage

The MCP client needs to be updated to pass questions as an array instead of a string.

### 2. Update Memory Bank MCP Server

The memory bank MCP server should handle both single questions and arrays gracefully.

## Implementation

### Fix 1: Update MCP Client

```python
# Before (incorrect):
await mcp_client.call_tool("ask_question", {
    "questions": "What is the capital of France?"
})

# After (correct):
await mcp_client.call_tool("ask_question", {
    "questions": ["What is the capital of France?"]
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

1. Test with single question: `["What is X?"]`
2. Test with multiple questions: `["What is X?", "What is Y?"]`
3. Verify no more "expected array, received string" errors

## Prevention

Add input validation in the MCP client to ensure questions are always passed as arrays.