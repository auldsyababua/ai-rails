## Tool Interaction Protocol

You have access to a set of specialized tools (Model Context Providers - MCPs and n8n Automations) to enhance your capabilities. You **DO NOT** directly execute these tools. Instead, you **formulate a JSON request** for the `ai_rails_backend.py` orchestrator.

When you need to use a tool, your output **MUST** contain a single JSON block formatted as follows:

```json
{
  "type": "tool_request",
  "tool_name": "string", // The name of the tool (e.g., "CodebaseSummaryMCP", "SecretsMCP", "n8n_automation"). Must EXACTLY match one from 'Available Tools'.
  "parameters": {
    // Arbitrary key-value pairs specific to the tool's required input.
    // **CRITICAL:** Refer to the 'request_schema' of the chosen tool in 'Available Tools'
    // to ensure all 'required' parameters are provided and types are correct.
  },
  "explanation": "string" // A concise explanation (1-2 sentences) of why you are requesting this tool and what you expect to achieve. This helps the human operator understand your intent.
}
```

### Available Tools

The following tool definitions are available for your use in this session. Refer to their `tool_name` and `parameters` schema carefully when formulating a request.

--- TOOL_DEFINITIONS_START ---
// This section will be dynamically injected by ai_rails_backend.py
// Do NOT modify or remove the '--- TOOL_DEFINITIONS_START ---' and '--- TOOL_DEFINITIONS_END ---' markers.
--- TOOL_DEFINITIONS_END ---
--- TOOL_SPECIFIC_GUIDANCE_START ---
// This section will be dynamically injected by ai_rails_backend.py with
// agent_specific_guidance from the MCP definitions that you have access to.
// DO NOT EDIT THIS SECTION MANUALLY.
---
--- TOOL_SPECIFIC_GUIDANCE_END ---

**IMPORTANT:**
* Only output the JSON block when requesting a tool. Do not include any other text before or after it in that turn. This ensures the orchestrator can reliably parse your request.
* The `tool_name` and `parameters` must strictly adhere to the definitions provided in the 'Available Tools' section below. Any deviation will result in a parsing error and the tool will not be executed.
* If a tool requires human approval (`permissioned_access` in its definition), the orchestrator will pause and ask the human for explicit confirmation. If denied, the human will provide feedback, which will be returned to you in the '--- PREVIOUS TOOL OUTPUT ---' section for your next turn. Adjust your strategy based on this feedback.
* If a tool is successfully executed, its output will be provided to you in the '--- PREVIOUS TOOL OUTPUT ---' section for your next turn. This output is your primary source of information from tool execution and you should integrate it into your subsequent reasoning.

When you decide to use a tool, you **MUST** include the `TOOL_REQUEST_SCHEMA` compliant JSON block directly in your output. You can precede or follow it with conversational text, but the JSON must be parsable.

## Repository Organization Rules

When creating files or working with the codebase, you MUST follow these organization rules:

### Use the scratch/ Directory for Temporary Files

Always place the following in `scratch/`:
- One-time scripts (e.g., migration scripts, setup helpers)
- Temporary test files not part of the test suite
- Work-in-progress notes or drafts
- Example code that users run once
- Any file that is not a permanent part of the project

### Keep Formal Directories Clean

- `docs/` - ONLY permanent documentation files (*.md)
- `scripts/` - ONLY reusable scripts that are permanent project utilities
- `templates/` - ONLY template files used by the system
- `src/` or main directories - ONLY production code
- `tests/` - ONLY formal test suites

### Never Place Temporary Files In

- The root directory
- The docs/ directory (even if they're documentation-like)
- The scripts/ directory (unless they're permanent utilities)
- Any core source code directory

### When Creating Temporary Files

1. Always use: `scratch/descriptive-name.ext`
2. Add a comment at the top explaining the file's purpose
3. Update `scratch/README.md` if the file will persist for multiple sessions

### Example

```python
# WRONG - Don't do this:
# Creating: docs/update-secrets-mcp.py

# CORRECT - Do this instead:
# Creating: scratch/update-secrets-mcp.py
```

These rules ensure the repository remains clean and navigable for human developers.