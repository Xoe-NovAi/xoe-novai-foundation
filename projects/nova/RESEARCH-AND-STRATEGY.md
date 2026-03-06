# Voice Assistant - Research, Strategy & Implementation Plan

**Date**: February 21, 2026  
**Status**: Comprehensive Research & Enhancement Phase

---

## Executive Summary

Research reveals **three distinct integration patterns** required for full IDE support:
1. **Cline**: MCP (Model Context Protocol) server - tools must be properly defined and exposed
2. **OpenCode**: Custom command interface - requires simple REPL with clear feedback
3. **Standalone CLI**: Native Python REPL - best UX for direct terminal use

Each has different requirements for tool discovery, invocation, and user feedback.

---

## Research Findings

### 1. Cline MCP Integration (Critical Issues Found)

**Problem**: MCP tools defined in Python but not properly exposed to Cline extension

**Key Findings**:
- Cline looks for tools defined in server response, not in Python classes
- Tool definitions need specific JSON schema format
- Tools must include: `name`, `description`, `inputSchema`
- Cline auto-discovers tools from `/tools/list` endpoint (if running MCP server)
- Simple Python tools won't work - need actual MCP server infrastructure

**Best Practice**:
- Use `mcp-cli` or similar MCP server helper
- Define tools with proper `CallTool` interface
- Expose via HTTP or stdio
- Include comprehensive schema for tool arguments

**Why It's Not Working**:
- Current implementation defines tools but doesn't actually RUN as MCP server
- Cline can't access the tools because they're not exposed via MCP protocol
- Missing: actual MCP server that implements tool calling

---

### 2. OpenCode Integration (Enhancement Opportunity)

**Problem**: OpenCode is a CODE EDITOR (like VS Code), not an MCP client

**Key Findings**:
- OpenCode is a full-featured IDE with built-in voice support
- Can run code directly and call external tools
- Best approach: Create OpenCode "extension" or use its CLI integration
- Simpler than Cline - doesn't require MCP protocol
- Can use subprocess, HTTP, or direct stdin/stdout

**Best Practice**:
- Integrate as external command tool
- Provide clear CLI interface with status feedback
- Use JSON output for structured responses
- Include real-time feedback mechanisms

**Current State**:
- OpenCode CLI works but UX could show more feedback/status
- Need to expose as callable command in OpenCode
- Command line interface is good, just needs polish

---

### 3. Standalone CLI (Works Well, Needs Polish)

**Findings**:
- Current implementation is solid
- REPL pattern is correct
- Needs: Better prompts, clearer help, input validation

**Best Practice**:
- Use `prompt_toolkit` for rich CLI (readline history, completion)
- Show context in prompt (current mode, status)
- Provide command suggestions
- Color-coded output for responses

---

## Knowledge Gaps Identified

### Gap 1: MCP Protocol Understanding
- **Issue**: MCP is not just tool definitions - it's a server protocol
- **Solution**: Implement actual MCP server using `mcp` library
- **Impact**: Enables true Cline integration

### Gap 2: Tool Discovery Mechanism
- **Issue**: Cline needs to discover tools - not just read them
- **Solution**: Implement tool registry endpoint
- **Impact**: Cline can auto-populate available tools

### Gap 3: IDE Integration Patterns
- **Issue**: Different IDEs expect different integrations
- **Solution**: Separate CLI for each IDE type
- **Impact**: Native experience in each environment

### Gap 4: Error Handling & Feedback
- **Issue**: No clear error messages or operation status
- **Solution**: Structured response format with status codes
- **Impact**: Better UX and debugging

### Gap 5: Command Parsing UX
- **Issue**: Current parsing is minimal
- **Solution**: Add command completion, suggestions, help
- **Impact**: Discoverability and ease of use

---

## Enhancement Strategy

### Phase 1: Fix Cline Integration ✓ PLAN

**Objective**: Make Cline MCP tools actually work

**Approach**:
1. Implement actual MCP server (not just tool definitions)
2. Use `mcp` Python library if available, or simple HTTP server
3. Expose tools with proper schema
4. Test Cline discovery and tool calling

**Implementation**:
- Create `mcp_server.py` - implements MCP protocol
- Update `ClineCLI` to start MCP server
- Define tools with full schema
- Add tool registry endpoint

---

### Phase 2: Enhance OpenCode UX ✓ PLAN

**Objective**: Improve OpenCode integration and user experience

**Approach**:
1. Add rich feedback (colors, status indicators)
2. Implement command completion
3. Show available commands on startup
4. Add command history
5. Better error messages

**Implementation**:
- Enhance `OpenCodeCLI` with status indicators
- Add structured JSON output
- Include help system
- Improve prompt display

---

### Phase 3: Polish Standalone CLI ✓ PLAN

**Objective**: Best-in-class terminal UX

**Approach**:
1. Use `prompt_toolkit` for enhanced REPL
2. Add command completion
3. Show help suggestions
4. Color-coded output
5. Command history

**Implementation**:
- Integrate `prompt_toolkit`
- Enhanced prompt with context
- Command suggestions
- Pretty printing

---

## Implementation Plan

### 1. MCP Server Implementation

**File**: `mcp_server.py` (NEW)

```python
# Proper MCP protocol implementation
# - Tool registry
# - Tool calling interface
# - Protocol compliance
# - HTTP or stdio interface
```

**File**: `ClineCLI` (ENHANCED)

```python
# - Starts actual MCP server
# - Registers tools properly
# - Implements tool calling
# - Handles MCP protocol
```

### 2. CLI Enhancement

**Files**:
- `cli_abstraction.py` - Base class enhancement
- `StandaloneCLI` - Add prompt_toolkit
- `OpenCodeCLI` - Add feedback/status
- `ClineCLI` - Add MCP server

### 3. Documentation

**Files**:
- `CLINE-INTEGRATION-GUIDE.md` - How to use with Cline
- `OPENCODE-INTEGRATION-GUIDE.md` - How to use with OpenCode
- `CLI-UX-GUIDE.md` - Terminal usage guide
- `MCP-IMPLEMENTATION.md` - Technical MCP details

### 4. Validation & Testing

**Tests**:
- MCP server responds to tool list request
- Cline can discover tools
- OpenCode can call commands with feedback
- Standalone CLI has good UX

---

## Best Practices Extracted

### 1. Tool Definition Best Practice
```
Every voice tool should include:
- name: unique identifier
- description: 1-2 sentence explanation
- inputSchema: JSON schema for arguments
- examples: usage examples
- category: grouping (voice, status, memory)
```

### 2. Command Parsing Best Practice
```
Support multiple formats:
- voice hello         # Simple format
- /voice hello        # Slash format
- voice --options    # Options support
Help should show all formats
```

### 3. Response Format Best Practice
```
Structured responses:
- Success responses: { status: "ok", data: ... }
- Error responses: { status: "error", error: ..., code: ... }
- Status feedback: { status: "processing", progress: ... }
```

### 4. UX Best Practice
```
CLI should provide:
- Context in prompt (mode, status)
- Command history
- Tab completion
- Clear help system
- Status indicators
- Exit hints
```

### 5. IDE Integration Best Practice
```
Each IDE needs:
- Native command format
- Proper error handling
- Feedback mechanism
- Tool discovery
- Command completion
```

---

## Technical Decisions

### Decision 1: MCP Server Approach
**Option A**: Use `mcp` library (requires pip install)
**Option B**: Implement simple HTTP wrapper
**Option C**: Use stdio-based MCP

**Chosen**: **Option B - HTTP wrapper**
- Reason: Simple, no new dependencies, debuggable
- Can proxy to actual tool execution
- Easy for testing

### Decision 2: CLI Enhancement Library
**Option A**: Add `prompt_toolkit` dependency
**Option B**: Simple readline enhancement
**Option C**: Keep current minimal approach

**Chosen**: **Option A - prompt_toolkit (optional)**
- Reason: Rich UX, history, completion
- Can be optional (falls back to simple REPL)
- Industry standard

### Decision 3: Response Format
**Option A**: Plain text responses
**Option B**: JSON only
**Option C**: Context-aware (JSON for machines, formatted for humans)

**Chosen**: **Option C - Context-aware**
- Reason: Humans need readable output
- Tools need structured data
- Format based on context

---

## Implementation Priorities

### Priority 1 (Critical): MCP Server
- [ ] Create `mcp_server.py`
- [ ] Implement tool registry
- [ ] Add HTTP wrapper
- [ ] Update ClineCLI

### Priority 2 (High): CLI Enhancement
- [ ] Add status indicators to OpenCodeCLI
- [ ] Implement command suggestions
- [ ] Improve error messages
- [ ] Add help system

### Priority 3 (Medium): UX Polish
- [ ] Add prompt_toolkit if desired
- [ ] Command completion
- [ ] Command history
- [ ] Pretty printing

### Priority 4 (Documentation)
- [ ] Cline integration guide
- [ ] OpenCode integration guide
- [ ] MCP protocol docs
- [ ] CLI UX guide

---

## Validation Criteria

### Cline Integration
- [ ] Cline discovers voice tools
- [ ] Tool descriptions show in Cline
- [ ] Voice commands execute
- [ ] Responses appear in Cline
- [ ] Error handling works

### OpenCode Integration
- [ ] Commands execute from terminal
- [ ] Status feedback displayed
- [ ] Help system works
- [ ] Error messages clear
- [ ] UX feels polished

### Standalone CLI
- [ ] Command history works
- [ ] Tab completion available
- [ ] Prompts show context
- [ ] Help is discoverable
- [ ] Responses are readable

---

## Risk Mitigation

### Risk 1: MCP Protocol Complexity
**Mitigation**: Start with simple HTTP wrapper, add protocol compliance incrementally

### Risk 2: Missing Dependencies
**Mitigation**: Make enhancements optional, graceful fallback to basic mode

### Risk 3: Breaking Changes
**Mitigation**: Keep existing CLI working, add enhancements without removing features

### Risk 4: Performance
**Mitigation**: MCP server should be lightweight, test latency

---

## Success Metrics

1. **Cline**: "Voice tools appear in Cline's tool list and execute correctly"
2. **OpenCode**: "Commands work and provide clear feedback"
3. **Standalone**: "REPL is pleasant to use with history and completion"
4. **Documentation**: "Users can set up each option in <5 minutes"
5. **Overall**: "All three options provide good UX"

---

## Next Steps

1. **Immediate**: Implement MCP server for Cline
2. **Short-term**: Enhance CLI feedback and status
3. **Medium-term**: Add UX polish and optional dependencies
4. **Long-term**: Create comprehensive integration guides

---

## Research Sources Used

- MCP (Model Context Protocol) official documentation
- OpenCode IDE documentation and community guides
- CLI UX best practices from industry standards
- REPL design patterns
- Voice command interfaces (Siri, Alexa patterns)
- Error handling in CLI applications

---

**Document Version**: 1.0  
**Last Updated**: February 21, 2026  
**Status**: Research Complete - Implementation Ready
