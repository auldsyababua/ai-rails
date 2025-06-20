# **Future Updates / Scratchpad**

This section serves as a living document for potential improvements and ideas.

* **Simple UI / Dashboard (App-like Web Controller \- MVP Priority):**  
  * **Goal:** A beautiful, simple, app-like experience to manage the "AI Rails" workflow, eliminating manual copy-pasting. This is an **MVP feature**.  
  * **Technology:** A Python web application (e.g., Flask, FastAPI with a lightweight frontend framework like HTMX, Alpine.js, or vanilla JS) running in a Docker container on your **NAS** (192.168.1.21) or **Workhorse** (10.0.0.2), accessible via your Nginx Proxy (192.168.1.3). This avoids Mac Mini localhost issues and centralizes UI hosting.  
  * **Features:**  
    * **Output Box:** Display the output from the previous step clearly, rendered as Markdown if applicable.  
    * **"Send to Next Agent" Buttons:** Automate the copy-pasting of current output as input to the next agent.  
    * **Tool Use Automation:** Buttons within the UI that, when clicked, trigger the execution of formulated MCP Query Requests or n8n Automation Requests via backend Python scripts. This eliminates manual copy-pasting for tools.  
    * **Diff Viewer:** An area to view code changes, diffs, and review reports.  
    * **Commit/Push Integration:** Buttons to trigger git commit and git push after code generation/review.  
    * **Log Viewer:** A dedicated panel to display the ai-rails.log in real-time, perhaps with filtering.  
    * **Template Manager:** A UI to view, edit, and manage agent system prompts and kickoff templates.  
    * **Agent Request Alert System (New):**  
      * When an MCP Query Request or n8n Automation Request is detected, a prominent UI alert (modal/notification) appears.  
      * Displays: Requesting Agent (Planner, Coder, etc.), full raw JSON request, explanation of the MCP/tool.  
      * Buttons: "Accept & Run Tool" (automates execution and feeds result to agent), "Deny & Send Custom Feedback" (opens input for human response to agent), "Deny & Stop Agent" (terminates current agent session).  
* **Command-Line Arguments / Quick Start Alias:**  
  * **Goal:** Allow bypassing interactive prompts for common workflows using command-line arguments.  
  * **Mechanism:** Enhance run\_workflow.sh to parse arguments like airails \<alias\_name\> \<project\_location\_or\_name\> \<takeover\_type\> "\<initial\_summary\>".  
  * **Error Handling:** If \<project\_location\_or\_name\> is given for a "new project" command and the directory already exists, the script should **reject with a message: "A project/directory with this name already exists. Please choose another name,"** then give a prompt for input of the new name (if interactive) or error out (if in non-interactive/alias mode). For "takeover" or "feature" modes, it would check for existence but not necessarily reject.  
* **Redis Support for Agent State Management:**  
  * **Goal:** Maintain conversation history and short-term memory across multiple agent turns and sessions without constantly re-pasting large contexts.  
  * **Mechanism:** Utilize a Redis instance (on Workhorse or NAS).  
  * The UI controller (or ai\_rails\_backend.py) would be responsible for serializing/deserializing conversation state to/from Redis.  
  * Agent system prompts would be updated to instruct them to leverage this "short-term memory" by referencing a unique session ID.  
* **Automated MCP call\_mcp.sh / call\_mcp.py and Response Parsing:**  
  * Develop a dedicated Python script (call\_mcp.py) that acts as a central handler for all MCP and n8n tool calls.  
  * It will take the agent's formulated JSON request, identify the mcp\_name, route the request to the correct Workhorse IP/port, handle API calls, and parse the response.  
  * It will then return the relevant context to the calling ai\_rails\_backend.py for injection into the LLM.  
* **Automated Local Codebase Indexing for CodebaseSummaryMCP:**  
  * Set up a daemon on the Workhorse (or NAS) that continuously indexes your project's codebase into a local vector database. This database would then be served by your custom CodebaseSummaryMCP.  
* **Dynamic Tool Description Injection (Refined):** Instead of hardcoding all tool descriptions in every agent prompt, the UI/backend could dynamically inject *only the relevant tool definitions* (from templates/mcp\_definitions/) into the system prompt for the active agent, further minimizing context window usage.  
* **Overseer Agent Detailed Explanation (New):**  
  * Refer to docs/overseer\_agent\_details.md for a comprehensive explanation of the Overseer Agent's architecture, anomaly detection strategies, context management (summarization), and UI integration (alert system, interruption mechanism). This will mostly recycle the detailed explanation provided in previous turns.
* **Centralized & Granular Tool Configuration (Enhanced `templates/mcp_definitions/`):**
  * **Goal:** To establish a single, highly maintainable source of truth for defining available tools (MCPs and n8n automations), their access permissions, and agent-specific usage guidance. This eliminates the need to manually update instructions within each agent's system prompt Markdown file whenever a tool is added, modified, or its usage guidance changes.
  * **Problem Solved:** Prevents scattered and potentially inconsistent tool usage instructions across multiple agent prompt templates, improving maintainability and reducing human error during updates.
  * **Mechanism:**
      * **Augmented MCP Definitions:** The JSON files within `templates/mcp_definitions/` will be enhanced to include new top-level fields:
          * `access_control`: A JSON object defining which `agent_role`s have access to this tool, and their permission level (e.g., `"free_access"` for direct use, `"permissioned_access"` for human-gated approval for sensitive operations like `SecretsMCP` for `ANTHROPIC_API_KEY`).
          * `agent_specific_guidance`: A JSON object where keys are `agent_role`s and values are Markdown strings providing specific instructions to that agent on *when* and *how* to best formulate a request for this particular tool.
      * **Backend Logic Refinement (`ai_rails_backend.py`):**
          * The `ai_rails_backend.py` will read these extended MCP definitions.
          * When constructing an agent's prompt, it will filter the tool list based on the current `agent_role`'s `access_control` for each tool.
          * For each accessible tool, it will dynamically inject not just the `tool_name`, `description`, and `request_schema`, but also the `agent_specific_guidance` relevant to the active agent into the "Available Tools" section of the prompt.
          * The backend will then enforce the `free_access` vs. `permissioned_access` logic for tool execution, especially critical for the `SecretsMCP`.
  * **Benefits:**
      * **Single Source of Truth:** All tool-related configurations and instructions live in one central place.
      * **Improved Maintainability:** Adding, modifying, or removing tools (or their usage guidelines) only requires updating their respective JSON definition, not multiple agent Markdown files.
      * **Enhanced Precision:** Agents receive highly tailored instructions for each tool, based on their specific role and the tool's intended use within that role.
      * **Scalability:** Easier to manage a growing number of agents and tools.
* **Integration of 3rd Party AI Code Review Agents:** Explore and implement dedicated MCPs to leverage external AI code review services (e.g., CodeRabbit, Diamond) for enhanced code quality and security analysis, with human-gated approval.