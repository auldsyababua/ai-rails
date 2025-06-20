# AI Rails Codebase Audit - Product Requirements Document

**Date**: December 2024  
**Auditor**: System Analysis  
**Version**: 1.0

## Executive Summary

This document presents a comprehensive audit of the AI Rails codebase, identifying critical issues that prevent the system from functioning as designed. The audit reveals fundamental integration problems between components, missing configuration elements, and incomplete implementations that require immediate attention.

## Table of Contents

1. [System Overview](#system-overview)
2. [Critical Issues](#critical-issues)
3. [High Priority Issues](#high-priority-issues)
4. [Medium Priority Issues](#medium-priority-issues)
5. [Proposed Solutions](#proposed-solutions)
6. [Implementation Timeline](#implementation-timeline)
7. [Testing Requirements](#testing-requirements)
8. [Future Enhancements](#future-enhancements)

## System Overview

AI Rails is designed as a human-centric, bounded AI engineering workflow system that prioritizes safety, transparency, and developer control. The system uses a "dumb orchestrator" approach with compartmentalized AI agents operating within strict boundaries.

### Key Components Analyzed
- `run_workflow.sh` - Shell script orchestrator
- `ai_rails_backend.py` - Python backend for LLM interaction
- `call_mcp.py` - MCP service dispatcher
- Agent templates in `templates/agents/`
- MCP definitions in `templates/mcp_definitions/`

## Critical Issues

### 1. Directory Path Mismatch

**Severity**: 🔴 CRITICAL  
**Impact**: Complete system failure - no agents can be loaded

**Details**:
- **Location**: `ai_rails_backend.py` lines 83, 227
- **Issue**: Code references `templates/agent/` (singular)
- **Reality**: Actual directory is `templates/agents/` (plural)
- **Error**: `FileNotFoundError` when attempting to load any agent

**Code Example**:
```python
# Current (BROKEN):
common_components_path = TEMPLATES_DIR / "agent" / "common_agent_components.md"
agent_template_path = TEMPLATES_DIR / "agent" / agent_template_filename

# Should be:
common_components_path = TEMPLATES_DIR / "agents" / "common_agent_components.md"
agent_template_path = TEMPLATES_DIR / "agents" / agent_template_filename
```

### 2. Missing Command-Line Argument Handling

**Severity**: 🔴 CRITICAL  
**Impact**: Shell script cannot communicate with Python backend

**Details**:
- **Location**: `ai_rails_backend.py` `__main__` block (lines 552-565)
- **Issue**: No `sys.argv` parsing implemented
- **Expected**: Shell passes `python3 script.py project_name workflow_type [plan_path]`
- **Reality**: Python script ignores all arguments

**Required Implementation**:
```python
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python ai_rails_backend.py <project_name> <workflow_type> [plan_path]")
        sys.exit(1)
    
    project_name = sys.argv[1]
    workflow_type = sys.argv[2]
    plan_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    
    main_workflow_loop(project_name, workflow_type, plan_path)
```

### 3. Incomplete MCP Definitions

**Severity**: 🔴 CRITICAL  
**Impact**: No agents can access any tools

**Details**:
- **Location**: All files in `templates/mcp_definitions/`
- **Missing Fields**:
  - `access_control` - Required by line 116 of `ai_rails_backend.py`
  - `agent_specific_guidance` - Required by line 122
- **Result**: Tool list remains empty for all agents

**Required Structure**:
```json
{
    "tool_name": "SecretsMCP",
    "description": "...",
    "access_control": {
        "Planning Agent": true,
        "Coder Agent": true,
        "Unit Tester Agent": false
    },
    "agent_specific_guidance": {
        "Planning Agent": "Use this to retrieve API keys for external services",
        "Coder Agent": "Request secrets only when implementing integrations"
    },
    "request_schema": {...},
    "response_format": "..."
}
```

## High Priority Issues

### 4. Missing Environment Configuration

**Severity**: 🟡 HIGH  
**Impact**: MCP services cannot be contacted

**Details**:
- No `.env` file exists in the project
- Required environment variables not documented
- Authentication tokens not configured

**Required Variables**:
```bash
# MCP Service URLs
CODEBASE_SUMMARY_MCP_URL=http://10.0.0.2:8003
SECRETS_MCP_URL=http://10.0.0.2:8004
MCP_SEQUENTIAL_THINKING_URL=http://10.0.0.2:8001
CONTEXT7_URL=http://10.0.0.2:8002
BRAVE_SEARCH_MCP_URL=http://10.0.0.2:8005
N8N_WEBHOOK_BASE_URL=http://192.168.1.3:80/n8n/webhook/

# Authentication
AI_RAILS_SECRETS_MCP_AUTH_TOKEN=your-auth-token-here

# Ollama Configuration
OLLAMA_BASE_URL=http://10.0.0.2:11434

# Claude API (optional)
ANTHROPIC_API_KEY=sk-ant-...
```

### 5. MCP Name Inconsistencies

**Severity**: 🟡 HIGH  
**Impact**: Tool requests fail with "Unknown tool" errors

**Details**:
- JSON definitions use one naming convention
- `call_mcp.py` expects different names
- No validation of tool names

**Examples**:
- JSON: `"tool_name": "SecretsMCP"`
- Code expects: Various formats (`Secrets_MCP`, `secrets-mcp`, etc.)

## Medium Priority Issues

### 6. Incomplete Error Handling

**Severity**: 🟡 MEDIUM  
**Impact**: Poor debugging experience, silent failures

**Areas Needing Improvement**:
- MCP connection failures
- Missing template files
- Invalid JSON in agent responses
- Network timeouts

### 7. Missing Integration Tests

**Severity**: 🟡 MEDIUM  
**Impact**: No automated verification of system functionality

**Required Tests**:
- End-to-end workflow execution
- Agent-MCP communication
- Error handling paths
- Template loading and injection

### 8. Documentation Gaps

**Severity**: 🟡 MEDIUM  
**Impact**: Difficult setup and troubleshooting

**Missing Documentation**:
- Complete setup guide with all dependencies
- Environment variable reference
- MCP deployment instructions
- Troubleshooting guide

## Proposed Solutions

### Solution 1: Fix Critical Path Issues

**Objective**: Make the system minimally functional

**Changes Required**:
1. Update all path references from `agent` to `agents`
2. Implement proper command-line argument parsing
3. Add required fields to all MCP definitions
4. Create comprehensive `.env.example` file
5. Add environment validation on startup

### Solution 2: Implement Robust Error Handling

**Objective**: Improve system reliability and debugging

**Changes Required**:
1. Add try-catch blocks around all external calls
2. Implement proper logging with levels
3. Add validation for all user inputs
4. Create custom exception classes
5. Add retry logic for network failures

### Solution 3: Complete MCP Integration

**Objective**: Enable full tool functionality

**Changes Required**:
1. Standardize MCP naming conventions
2. Add MCP discovery mechanism
3. Implement health checks for MCPs
4. Add MCP configuration validation
5. Create MCP testing utilities

## Implementation Timeline

### Week 1: Critical Fixes
- Day 1-2: Fix path issues and argument parsing
- Day 3-4: Update MCP definitions
- Day 5: Create environment configuration

### Week 2: Integration & Testing
- Day 1-2: Implement error handling
- Day 3-4: Add integration tests
- Day 5: Documentation updates

### Week 3: Enhancements
- Day 1-2: Overseer Agent implementation
- Day 3-4: UI/Dashboard prototype
- Day 5: Performance optimization

## Testing Requirements

### Unit Tests
- Template loading functionality
- MCP definition parsing
- Command-line argument handling
- Error handling paths

### Integration Tests
- Full workflow execution (new project, feature update, execution)
- Agent-MCP communication
- Multi-agent coordination
- Error recovery scenarios

### System Tests
- Performance under load
- Network failure handling
- Security validation
- Cross-platform compatibility

## Future Enhancements

### 1. Overseer Agent
- Monitor other agents for anomalies
- Provide additional safety layer
- Alert on suspicious behavior

### 2. Web UI/Dashboard
- Replace command-line interface
- Real-time agent monitoring
- Visual workflow management
- Approval interface for tool requests

### 3. Enhanced Security
- Implement proper SecretsMCP authentication
- Add rate limiting for API calls
- Implement audit logging
- Add encryption for sensitive data

### 4. Advanced Features
- Multi-model support (beyond Ollama/Claude)
- Parallel agent execution
- Workflow templates
- Plugin system for custom agents

### 5. Deployment Improvements
- Complete Docker containerization
- Kubernetes deployment options
- Auto-scaling for MCP services
- Monitoring and alerting

## Conclusion

The AI Rails system has a solid architectural foundation but requires critical fixes before it can function as designed. The issues identified are solvable with focused development effort. Priority should be given to the critical path fixes that prevent basic operation, followed by robustness improvements and feature enhancements.

## Appendix: Code Snippets

### A. Fixed Command-Line Parsing
```python
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python ai_rails_backend.py <project_name> <workflow_type> [plan_path]")
        sys.exit(1)
    
    project_name = sys.argv[1]
    workflow_type = sys.argv[2]
    
    if workflow_type == "execution" and len(sys.argv) < 4:
        print("Error: Execution workflow requires a plan path")
        sys.exit(1)
    
    plan_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    
    try:
        main_workflow_loop(project_name, workflow_type, plan_path)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
```

### B. MCP Definition with Access Control
```json
{
    "tool_name": "CodebaseSummaryMCP",
    "description": "Provides summary or detailed context about the codebase",
    "access_control": {
        "Planning Agent": true,
        "Coder Agent": true,
        "Unit Tester Agent": true,
        "Debugger Agent": true,
        "Documentation Agent": true,
        "Code Review Agent": true,
        "Refactor Agent": true,
        "n8n Flow Creator Agent": false,
        "Overseer Agent": true
    },
    "agent_specific_guidance": {
        "Planning Agent": "Use this to understand the current project structure before creating plans",
        "Coder Agent": "Query existing code patterns and conventions before implementing new features",
        "Unit Tester Agent": "Examine existing test patterns and coverage before writing new tests"
    },
    "request_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query about the codebase"
            },
            "path": {
                "type": "string",
                "description": "Optional: specific path to focus on",
                "default": "."
            }
        },
        "required": ["query"]
    },
    "response_format": "Markdown formatted text with code examples"
}
```

### C. Environment Validation
```python
def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = [
        "OLLAMA_BASE_URL",
        "AI_RAILS_SECRETS_MCP_AUTH_TOKEN"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment")
        return False
    
    return True
```

---

End of Audit Report