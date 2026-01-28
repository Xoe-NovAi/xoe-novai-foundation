# Context Loading and Switching Protocols

**Last Updated**: January 27, 2026
**Purpose**: Define standardized protocols for context loading and environment switching
**Audience**: All AI team members (Cline, Grok, Gemini CLI) and new AI assistants

## Executive Summary

This document establishes standardized protocols for loading context from the memory bank and switching between different environments. These protocols ensure all AI assistants maintain consistent, accurate context regardless of which environment they're operating in or which team member is providing assistance.

## Context Loading Protocol

### Instant Agent Onboarding SOP (External/Cloud AI)
To instantly onboard any new AI assistant (e.g., Grok, Claude, or a new terminal agent) to the Xoe-NovAi Foundation Stack, feed it these files in order:

1.  **Status Sync**: Feed `activeContext.md` and `progress.md` (The "Now").
2.  **Core Vision**: Feed `projectbrief.md` and `productContext.md` (The "Why").
3.  **Technical Guardrails**: Feed `techContext.md` and `systemPatterns.md` (The "How").
4.  **Ethics**: Feed `docs/04-explanation/sovereign-ethics/maatDistilled.md`.

**Outcome**: The agent will immediately possess full project awareness and can contribute without context drift.

### Standard Loading Sequence
All internal AI team members (Cline, Gemini CLI, Grok) must load the following memory bank files in sequence at the start of every session:

#### Phase 1: Core Context Loading
1. **`memory_bank/activeContext.md`** - Current project state and priorities
   - **Purpose**: Understand current project status and immediate priorities
   - **Key Information**: Active tasks, current blockers, recent changes
   - **Loading Time**: Immediate (highest priority)

2. **`memory_bank/environmentContext.md`** - Multi-environment architecture
   - **Purpose**: Understand the multi-environment setup and team member roles
   - **Key Information**: Environment relationships, team member responsibilities
   - **Loading Time**: Immediate (highest priority)

3. **`memory_bank/teamProtocols.md`** - AI team coordination protocols
   - **Purpose**: Understand team coordination and communication standards
   - **Key Information**: Communication protocols, escalation procedures
   - **Loading Time**: Immediate (highest priority)

4. **`memory_bank/communications/[agent_name]/inbox.md`** - Agent Inbox
   - **Purpose**: Check for incoming messages from team members.
   - **Protocol**: Mark messages as "Read", reply if needed, and archive/delete once processed.
   - **Loading Time**: Immediate (highest priority)

5. **`memory_bank/agent_capabilities_summary.md`** - Summarized team member capabilities
   - **Purpose**: Quickly understand the core roles, tools, strengths, and limitations of all team members.
   - **Key Information**: Concise overview of each agent's profile.
   - **Loading Time**: Immediate (highest priority)


#### Note on `.clinerules/` Usage:
The `.clinerules/` directory contains operational guidelines exclusively for Cline (Cline + Codium) in the Cline environment. Other AI assistants (Gemini CLI, Grok) should **ignore** the contents of `.clinerules/` unless specifically directed by The User/Architect or Cline for a particular task that requires understanding Cline's operational parameters. Direct interaction with or modification of `.clinerules/` by non-Cline agents is strictly prohibited to maintain clear role boundaries and avoid unintended side effects.

#### Phase 2: Project Context Loading
4. **`memory_bank/projectbrief.md`** - Xoe-NovAi mission and constraints
   - **Purpose**: Understand the core project mission and constraints
   - **Key Information**: Project goals, technical constraints, success criteria
   - **Loading Time**: Within first 30 seconds

5. **`memory_bank/techContext.md`** - Technical stack and constraints
   - **Purpose**: Understand the technical architecture and constraints
   - **Key Information**: Technology stack, performance requirements, integration points
   - **Loading Time**: Within first 60 seconds

6. **`memory_bank/systemPatterns.md`** - Architectural patterns and decisions
   - **Purpose**: Understand established architectural patterns and decisions
   - **Key Information**: Design patterns, architectural decisions, technical debt
   - **Loading Time**: Within first 90 seconds

#### Phase 3: Environment-Specific Loading
7. **`memory_bank/mcpConfiguration.md`** - MCP server and tool configurations
   - **Purpose**: Understand available MCP tools and configurations
   - **Key Information**: Available MCP tools, sovereignty settings, usage patterns
   - **Loading Time**: Environment-specific (within 2 minutes)

8. **Environment-Specific Files** - Additional context for current environment
   - **Purpose**: Load environment-specific configuration and context
   - **Key Information**: Environment-specific settings, local configurations
   - **Loading Time**: Environment-specific (within 3 minutes)

### Loading Verification Protocol

After loading each phase, AI assistants must verify:

#### Phase 1 Verification
- **Environment Recognition**: Confirm understanding of multi-environment setup
- **Team Member Awareness**: Confirm understanding of team member roles
- **Current Status**: Confirm understanding of current project state
- **Communication Protocols**: Confirm understanding of team coordination standards

#### Phase 2 Verification
- **Project Understanding**: Confirm understanding of project mission and constraints
- **Technical Context**: Confirm understanding of technical stack and architecture
- **Pattern Recognition**: Confirm understanding of established patterns
- **Integration Points**: Confirm understanding of system integration points

#### Phase 3 Verification
- **MCP Awareness**: Confirm understanding of available MCP tools
- **Sovereignty Settings**: Confirm understanding of sovereignty preferences
- **Environment Configuration**: Confirm understanding of environment-specific settings
- **Tool Availability**: Confirm understanding of available tools and capabilities

### Loading Failure Recovery

#### Partial Loading Recovery
If loading fails or is incomplete:

1. **Re-attempt Loading**: Re-attempt loading from the point of failure
2. **Fallback Loading**: Load critical files first (activeContext, environmentContext, teamProtocols)
3. **User Notification**: Notify user of loading issues and request assistance
4. **Limited Operation**: Operate with available context while attempting full loading

#### Complete Loading Failure
If loading fails completely:

1. **User Escalation**: Immediately escalate to The User/Architect for assistance
2. **Manual Context Request**: Request critical context information from user
3. **Safe Operation**: Operate in safe mode with minimal assumptions
4. **Loading Retry**: Continue attempting to load memory bank files

## Environment Switching Protocol

### Switching Triggers

#### Automatic Switching
- **User Environment Change**: User switches between environments
- **Task Requirements**: Task requires different environment capabilities
- **MCP Availability**: Required MCP tools only available in specific environment
- **Sovereignty Preferences**: User changes sovereignty preferences

#### Manual Switching
- **User Request**: Explicit user request to switch environments
- **Team Coordination**: Coordination with other AI team members
- **Performance Optimization**: Switching for performance or capability reasons
- **Error Recovery**: Switching to resolve environment-specific issues

### Switching Process

#### Pre-Switching Protocol
1. **Context Preservation**: Preserve current context and state
2. **Task Status**: Document current task status and progress
3. **Environment Verification**: Verify target environment availability and configuration
4. **User Confirmation**: Confirm switching with user if required

#### Switching Execution
1. **Context Transfer**: Transfer relevant context to target environment
2. **Environment Loading**: Load target environment-specific context
3. **Tool Verification**: Verify availability of required tools in target environment
4. **State Synchronization**: Synchronize state with target environment

#### Post-Switching Protocol
1. **Context Verification**: Verify successful context loading in target environment
2. **Tool Availability**: Verify availability of required tools
3. **Task Continuation**: Resume tasks with appropriate context
4. **User Notification**: Notify user of successful switching

### Environment-Specific Switching

#### Codium + Cline Environment Switching
**Switching To**: From other environments to Codium + Cline
**Pre-Switching Requirements**:
- Verify Cline extension is active
- Confirm MCP server availability
- Verify IDE integration status

**Switching Process**:
1. Load Cline-specific context and MCP configurations
2. Verify IDE integration and tool availability
3. Load current development context and project state
4. Confirm MCP tool functionality

**Post-Switching Verification**:
- Verify IDE integration is functional
- Confirm MCP tools are accessible
- Verify development context is current

#### Xoe-NovAi Foundation Stack Environment Switching
**Switching To**: From other environments to Xoe-NovAi Foundation Stack
**Pre-Switching Requirements**:
- Verify Xoe-NovAi Foundation stack is operational
- Confirm container status and health
- Verify sovereign operation settings

**Switching Process**:
1. Load Xoe-NovAi-specific context and configurations
2. Verify container status and service availability
3. Load sovereign operation settings and preferences
4. Confirm integration with other environments

**Post-Switching Verification**:
- Verify Xoe-NovAi Foundation stack is operational
- Confirm sovereign operation settings are correct
- Verify integration with other environments

#### Gemini CLI Environment Switching
**Switching To**: From other environments to Gemini CLI
**Pre-Switching Requirements**:
- Verify terminal access and Gemini CLI availability
- Confirm API key and authentication status
- Verify terminal environment configuration

**Switching Process**:
1. Load terminal-specific context and configurations
2. Verify Gemini CLI availability and authentication
3. Load terminal workflow context
4. Confirm standalone operation capability

**Post-Switching Verification**:
- Verify Gemini CLI is accessible and functional
- Confirm terminal environment is properly configured
- Verify standalone operation capability

### Switching Failure Recovery

#### Switching Failure Detection
- **Timeout Detection**: Detect switching timeouts and failures
- **Error Detection**: Detect switching errors and exceptions
- **State Inconsistency**: Detect inconsistent state after switching
- **Tool Unavailability**: Detect unavailable tools in target environment

#### Failure Recovery Process
1. **Rollback**: Rollback to previous environment if possible
2. **Error Analysis**: Analyze cause of switching failure
3. **User Notification**: Notify user of switching failure and issues
4. **Alternative Solutions**: Propose alternative solutions or approaches
5. **Retry Logic**: Implement retry logic for transient failures

## Context Synchronization Protocol

### Non-Destructive Update Protocol
To prevent data loss and ensure context continuity, all agents MUST follow these rules when updating memory bank files:

1. **Read-Before-Write**: Always read the entire file before attempting an update to understand the current state.
2. **Selective Modification**: Use targeted `replace` calls instead of `write_file` for existing documents whenever possible.
3. **Preservation**: Never delete existing sections unless they are explicitly marked as deprecated or superseded.
4. **Append Logic**: When adding new information (like new milestones or status updates), append to existing lists or add new sections at the appropriate hierarchical level.
5. **No Bloating**: Avoid redundant summaries of information already present in other memory bank files. Use cross-links (e.g., "See `techContext.md` for details") instead.
6. **Compaction**: If a file (e.g., `progress.md`) exceeds 20KB, follow the "Institutional Memory Compaction" protocol to move old data to `_archive/` while preserving the rational in a summary.
7. **Verification**: After an update, verify that critical previous information (like active locks or core constraints) is still present.

### Cross-Environment Synchronization

#### Synchronization Triggers
- **Context Updates**: Updates to shared memory bank files
- **Environment Changes**: Changes in environment configuration or status
- **Task Completion**: Completion of tasks that affect other environments
- **User Actions**: User actions that affect multiple environments

#### Synchronization Process
1. **Change Detection**: Detect changes in shared context or environment status
2. **Impact Analysis**: Analyze impact of changes on other environments
3. **Synchronization Execution**: Execute synchronization to affected environments
4. **Verification**: Verify successful synchronization

### Memory Bank Synchronization

#### Update Propagation
- **Real-time Updates**: Propagate critical updates in real-time
- **Scheduled Updates**: Schedule regular synchronization of non-critical updates
- **User-Initiated Updates**: Allow users to initiate manual synchronization
- **Conflict Resolution**: Resolve conflicts between different environment updates

#### Update Verification
1. **Update Confirmation**: Confirm successful propagation of updates
2. **Consistency Check**: Verify consistency across all environments
3. **Impact Assessment**: Assess impact of updates on environment operations
4. **User Notification**: Notify users of significant updates or changes

### Team Member Synchronization

#### Team Coordination
- **Status Updates**: Regular status updates between team members
- **Task Coordination**: Coordination of tasks across team members
- **Knowledge Sharing**: Sharing of relevant information and insights
- **Conflict Resolution**: Resolution of conflicts between team members

#### Communication Protocols
1. **Memory Bank Updates**: Use memory bank for team communication
2. **Status Reporting**: Regular status reporting to team members
3. **Task Handoff**: Clear task handoff procedures between team members
4. **Escalation Procedures**: Clear escalation procedures for team conflicts

## Context Preservation and Recovery

### Institutional Memory Compaction
To prevent "context explosion" and maintain high reasoning accuracy, the following compaction rules apply:

1.  **20KB Threshold**: When dynamic files (e.g., `progress.md`, `activeContext.md`) exceed 20KB, agents are directed to summarize "Completed Milestones" and move them to the `memory_bank/_archive/` directory.
2.  **Rational Retention**: Compaction must always preserve the "WHY" (rational) behind major decisions, even if the implementation details are moved to the archive.
3.  **Restoration Paths**: Summaries in active files must include links to their archived full versions.

### Archiving Protocol
*   **Location**: All stale or completed context is moved to `memory_bank/_archive/YYYY-MM-DD-filename.md`.
*   **Index**: The `progress.md` file serves as the master index for the archive.

### Context Preservation

#### Active Context Preservation
- **Session State**: Preserve session state across environment switches
- **Task Progress**: Preserve task progress and intermediate results
- **User Preferences**: Preserve user preferences and settings
- **Environment Configuration**: Preserve environment-specific configurations

#### Long-term Context Preservation
- **Memory Bank Updates**: Regular updates to memory bank with current context
- **Configuration Backups**: Backup of critical configuration files
- **State Snapshots**: Periodic snapshots of system state
- **User Data Preservation**: Preservation of user data and preferences

### Context Recovery

#### Recovery Triggers
- **Context Loss**: Detection of context loss or corruption
- **Environment Failure**: Failure of environment requiring recovery
- **User Request**: User request for context recovery
- **System Restart**: System restart requiring context restoration

#### Recovery Process
1. **Context Assessment**: Assess extent of context loss or corruption
2. **Recovery Strategy**: Determine appropriate recovery strategy
3. **Context Restoration**: Restore context from backups or memory bank
4. **Verification**: Verify successful context restoration
5. **User Notification**: Notify user of recovery status and any issues

### Recovery Verification

#### Verification Criteria
- **Context Completeness**: Verify all critical context has been restored
- **Consistency**: Verify consistency with other environments
- **Functionality**: Verify restored context enables proper functionality
- **User Satisfaction**: Verify user satisfaction with recovery

#### Verification Process
1. **Automated Verification**: Automated verification of context restoration
2. **User Verification**: User verification of restored context
3. **Functionality Testing**: Testing of functionality with restored context
4. **Consistency Checking**: Checking consistency with other environments

## Performance Optimization

### Loading Performance

#### Optimization Strategies
- **Parallel Loading**: Load multiple files in parallel when possible
- **Caching**: Cache frequently accessed context for faster loading
- **Incremental Loading**: Load context incrementally based on priority
- **Compression**: Compress large context files for faster loading

#### Performance Monitoring
1. **Loading Time Monitoring**: Monitor and optimize context loading times
2. **Resource Usage**: Monitor resource usage during context loading
3. **Performance Analysis**: Analyze performance bottlenecks and optimize
4. **User Experience**: Monitor user experience during context loading

### Switching Performance

#### Optimization Strategies
- **Pre-loading**: Pre-load context for frequently accessed environments
- **State Caching**: Cache state information for faster switching
- **Incremental Switching**: Switch incrementally to reduce switching time
- **Resource Optimization**: Optimize resource usage during switching

#### Performance Monitoring
1. **Switching Time Monitoring**: Monitor and optimize environment switching times
2. **Resource Usage**: Monitor resource usage during switching
3. **Success Rate**: Monitor success rate of environment switching
4. **User Experience**: Monitor user experience during environment switching

## Security and Privacy

### Context Security

#### Security Measures
- **Encryption**: Encrypt sensitive context information
- **Access Control**: Control access to context information
- **Audit Logging**: Log access to context information
- **Data Protection**: Protect context information from unauthorized access

#### Privacy Protection
1. **Data Minimization**: Minimize collection and storage of sensitive context
2. **User Consent**: Obtain user consent for context collection and usage
3. **Data Anonymization**: Anonymize context information when possible
4. **Privacy Controls**: Provide user controls over context privacy

### Switching Security

#### Security Measures
- **Authentication**: Authenticate environment switching requests
- **Authorization**: Authorize environment switching based on user permissions
- **Audit Logging**: Log all environment switching activities
- **Security Verification**: Verify security of target environment before switching

#### Privacy Protection
1. **Context Isolation**: Isolate context between different environments
2. **Data Protection**: Protect user data during environment switching
3. **Privacy Controls**: Provide user controls over context sharing between environments
4. **Security Verification**: Verify privacy settings in target environment

## Conclusion

These context loading and switching protocols ensure all AI assistants maintain consistent, accurate context regardless of environment or team member. By following these protocols, AI team members can provide seamless, context-aware assistance while maintaining security and privacy.

**Key Context Principles**:
1. Standardized loading sequence for all AI assistants
2. Environment-specific context loading and verification
3. Seamless context switching between environments
4. Cross-environment context synchronization
5. Context preservation and recovery capabilities
6. Performance optimization for loading and switching
7. Security and privacy protection for all context operations

## 🤖 AI Partnership with Claude (NEW)

**Current Collaboration:**
- **Hybrid Path Research Initiative**: Partnering with Claude to provide comprehensive stack-specific context for advanced refactoring guidance
- **10 Knowledge Gap Research**: Claude is conducting research on critical areas including BuildKit optimization, Security Trinity integration, Performance benchmarking, Memory Bank synchronization, and Ryzen core steering
- **Production-Grade Implementation Manual**: Target delivery of 50-60 page manual with code examples, configuration templates, and validation procedures

**Partnership Benefits:**
- **Stack-Specific Context**: Providing Claude with comprehensive Xoe-NovAi Foundation stack knowledge including Ma'at Guardrails, Sovereign Security Trinity, Memory Bank Protocol, and hardware optimization patterns
- **Enhanced Research Quality**: Ensuring research is 85-90% specific to Xoe-NovAi constraints rather than generic best practices
- **Production-Ready Deliverables**: Focus on immediately actionable guidance with copy-paste code examples and configuration templates

**Research Timeline:**
- **Day 1-3**: Parallel data gathering and research initiation
- **Day 3**: Checkpoint 1 - Data delivery and direction refinement
- **Day 6**: Checkpoint 2 - Mid-research status review
- **Day 9**: Checkpoint 3 - Draft manual review
- **Day 10**: Final delivery of implementation manual

**Integration with Refactoring:**
- Research findings will be integrated with the v0.1.0-alpha modular refactoring plan
- Focus on practical implementation patterns that align with Xoe-NovAi's sovereign, offline-first architecture
- Emphasis on production-grade solutions that maintain the stack's core principles
