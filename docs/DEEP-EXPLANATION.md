# **AI Rails: A Human-Centric, Bounded AI Engineering Workflow**

**Version:** 1.4  
**Date:** June 19, 2025  
**Author:** Gemini (with user collaboration)

#### **1\. Philosophy & Core Principles**

The "AI Rails" architecture is designed for high-performance, precise, and auditable AI-assisted software development. It prioritizes human control, transparency, and safety by adopting a "dumb orchestrator" model and strictly bounding AI agent capabilities.

* **Human-as-Orchestrator (You):** The ultimate decision-maker, director, and quality gate. All critical decisions and transitions between phases are human-gated.  
* **Dumb Orchestrator Script (run\_workflow.sh / Future UI Backend):** This core component is a purely rule-based state machine at the *workflow decision level*. It contains *zero* AI decision-making. Its sole purpose is to guide the human operator, presenting choices, dictating input/output paths, defining the sequence of operations, and *programmatically interacting with LLMs and tools*. This prevents any single AI from accumulating "god mode" control over the *workflow itself*.  
  * **Implementation Language:** The core backend orchestration and UI logic will primarily be built using **Python** due to its maintainability and proficiency of LLMs in writing it. The run\_workflow.sh script will evolve into a bootstrap/orchestrator for these Python components.  
* **Bounded & Compartmentalized Agents (AI on Rails):** Each AI agent (e.g., Planner, Coder, Tester, Overseer) is defined by a rigid system prompt (.md file in templates/). These prompts act as strict "rails," confining the AI's intelligence to a specific domain (e.g., planning, coding, testing, anomaly detection) and preventing it from hallucinating beyond its defined role, making autonomous workflow decisions, or engaging in unauthorized actions.  
* **Explicit Human-in-the-Loop:** Mandatory human review and approval checkpoints are built into the workflow. This serves as a vital circuit breaker against unintended AI behavior, mesa-optimization, and ensures human "taste" and expertise are central. This includes explicit human approval for agent-requested MCP queries or tool executions, and for responding to Overseer Agent alerts.  
* **File-Based Communication Protocol:** All communication between different workflow stages and agents is mediated by structured files (Markdown, JSON) saved to disk. An agent's output is saved to a file, reviewed by the human, and then becomes the explicit input for the next stage or agent. This provides transparency and debuggability.  
* **Transparency & Auditability (Logging):** All significant interactions, inputs, and outputs within the workflow are logged to a dedicated, human-readable file, managed solely by the run\_workflow.sh script/UI backend. This prevents agents from "gaming" their own logs, providing an objective record of their actions and outputs.  
* **Compounding Engineering:** The architecture promotes the continuous improvement of templates, prompts, and the guiding script itself, making future development efforts more efficient and reliable.  
* **Hybrid LLM Strategy:** Leverages powerful local LLMs (Qwen2.5-coder:32b) for default operation and utilizes more capable but potentially costlier remote LLMs (Claude Opus) as a strategic fallback for complex or "hairy" problems. The Overseer Agent will typically run on a different, potentially higher-capability, model to provide a fresh perspective.

#### **2\. Architectural Components**

The system is distributed across your Mac Mini (control plane) and AI Workhorse (inference & services).

* **Human Operator (You):**  
  * **Role:** The ultimate orchestrator, decision-maker, and quality gate. You interact with the run\_workflow.sh script/UI, review agent outputs, and approve/deny agent-initiated actions or context requests. You also respond to alerts from the Overseer Agent.  
  * **Device:** Mac Mini M4 (192.168.1.209 / 10.0.0.1)  
* **AI Rails Repository (\~/Desktop/projects/ai-engineering-workflow/ on Mac Mini):**  
  * **run\_workflow.sh:** The initial "Dumb Orchestrator" script. This will bootstrap and orchestrate Python backend scripts.  
  * **ai\_rails\_backend.py (New):** The primary Python script handling LLM API calls, output parsing, log management, and interaction with MCPs/tools. This backend will also communicate with the Overseer Agent.  
  * **templates/:** Stores all bounded AI agent system prompts (e.g., planning\_agent\_system\_prompt.md, coder\_agent\_system\_prompt.md), initial kickoff templates (new\_project\_kickoff\_template.md, feature\_update\_kickoff\_template.md, takeover\_project\_kickoff\_template.md), and external tool definitions.  
  * **templates/mcp\_definitions/:** Stores modular JSON definitions for each available MCP, to be dynamically injected into agent prompts by the backend.  
  * **output/:** Directory for storing all generated outputs (plans, code snippets, test reports, debug logs, review reports) from AI agent interactions.  
  * **log/:** A dedicated directory for ai-rails.log which records all script actions and key human-AI interactions.  
* **AI Agent Clients (Managed Programmatically by ai\_rails\_backend.py / UI Backend):**  
  * **Local LLM Interaction:** ai\_rails\_backend.py will make direct API calls to your Ollama server on the Workhorse for Qwen2.5-coder:32b.  
  * **Remote LLM Interaction:** ai\_rails\_backend.py will use a Python client for Claude 4 Opus (either directly via API or by programmatically interacting with Claude Code CLI if direct API is not preferred for specific reasons).  
* **AI Workhorse (10.0.0.2 \- 192.168.1.199):**  
  * **Local LLM Inference Engine:**  
    * **Ollama Server:** Hosts and serves your qwen2.5-coder:32b and other local models. Accessible via network (e.g., http://10.0.0.2:11434).  
  * **Dynamic MCP Server Layer (Existing & Custom Implementations):**  
    * **MCP Servers:** Independent, specialized microservices running on the Workhorse, offering specific contextual data or limited, controlled actions.  
    * **Knowledge-Based MCPs:** Provide up-to-date, specialized information. Examples:  
      * MCP-Sequential-Thinking (e.g., from glama.ai): Provides structured reasoning and breakdown of tasks.  
      * Context7 (e.g., from Upstash/GitHub): Provides vector-database backed context retrieval for docs/memory.  
      * **CodebaseSummaryMCP (Custom):** A dedicated MCP for providing summarized or indexed information about your local codebase. This would be a service you run on the Workhorse, potentially indexing files from your NAS or synced directories.  
      * **SecretsMCP (Custom):** A dedicated MCP for securely managing and serving environment variables and API keys to agents.  
    * **Action-Oriented MCPs (Future):** (e.g., "Database Change MCP", "File System Write MCP"). These would expose highly constrained APIs for controlled execution of specific, potentially impactful actions.  
    * **API Interface:** Exposed via HTTP (e.g., http://10.0.0.2:8001/query, http://10.0.0.2:8002/context, http://10.0.0.2:8003/code\_summary, http://10.0.0.2:8004/get\_secret).  
    * **Embedded Vector Database:** Used by Context7 and custom MCPs for efficient context retrieval.  
  * **n8n Automation Engine:** Your self-hosted n8n instance, accessible over the network (e.g., http://192.168.1.3:80/n8n via Nginx Proxy).

#### **3\. Communication & Control Flow**

\+----------------+      \+--------------------+      \+---------------------------------+  
|   Human        |\<-----|  AI Rails Repo     |\<----\>|         AI Workhorse            |  
| (Mac Mini)     |      |  (Mac Mini)        |      | (10.0.0.2 / 192.168.1.199)      |  
|                |      |                    |      |                                 |  
|  \- Reviews     |      | \- \`run\_workflow.sh\`|      |  \- Ollama Server (Qwen:32b)     |  
|  \- Approves/   |      |    (Dumb Orchestrator)    |  \- MCP Servers (e.g., :8001, :8002) |  
|    Denies      |      | \- \`templates/\`     |      |  \- N8n Automation Engine        |  
|                |      | \- \`output/\`        |      |    (via NAS/Nginx)              |  
|                |      | \- \`log/\`           |      |  \- Embedded Vector DBs (for MCPs)|  
|                |      \+---------^----------+      \+---------------------------------+  
|                |                |  
|                |                | Orchestrates  
|                |                | LLM/Tool Calls  
\+------^---------+                |  
       |                          |  
       |  Automated Prompt/Input Passing  
       |  Automated Output Capture  
       |  
\+------v------------------------------------+  
|  LLM Client Interaction (Programmatic)   |  
|                                            |  
|  \- \*\*Default:\*\* Ollama API Calls (to       |  
|    Workhorse:11434 for Qwen:32b)           |  
|  \- \*\*Fallback:\*\* Claude API Calls (to      |  
|    Anthropic API via \`claude\` CLI)         |  
\+--------------------------------------------+

**Workflow Summary:**

1. **run\_workflow.sh (Mac Mini):** Initiates the workflow. It can accept command-line arguments (e.g., airails new-project my-app "Create a mobile app for X") to bypass interactive prompts, or guide the human through choices.  
2. **Human (Mac Mini) / run\_workflow.sh:** Provides custom inputs (project name, initial summary, etc.). For templates with blanks, the script/UI will ask the human to write and enter the content.  
3. **ai\_rails\_backend.py (Mac Mini):**  
   * Reads the relevant Agent System Prompt from templates/.  
   * Reads the task-specific input (from files or command-line args).  
   * **Dynamically loads MCP definitions** (from templates/mcp\_definitions/) and injects relevant portions into the LLM's system prompt.  
   * Makes a programmatic API call to the chosen LLM (Ollama on Workhorse or Claude).  
4. **AI Agent (Qwen/Claude):** Processes the prompt, generates output (plan, code, review, etc.) according to its bounded system prompt. If the agent formulates an MCP query or tool request (e.g., MCP Query Request, n8n Automation Request), this is embedded within its output.  
5. **ai\_rails\_backend.py (Mac Mini):**  
   * Captures the AI's output directly.  
   * Saves the AI's output to a designated file in the output/ directory.  
   * **Detects any embedded MCP Query Request or n8n Automation Request** within the AI's output.  
6. **Human Gating for Agent Requests (Future UI / ai\_rails\_backend.py):**  
   * If an MCP/tool request is detected, the UI (or ai\_rails\_backend.py in terminal mode) will *pause* and present a clear "alert" to the human:  
     * Which agent made the request.  
     * The full "naked request" (the raw JSON formulated by the agent).  
     * A clear explanation of what the MCP/tool is expected to do.  
   * **Accept/Deny Options:**  
     * **Accept:** If you accept, ai\_rails\_backend.py triggers a backend execution (e.g., via call\_mcp.py for MCPs, or direct API call for n8n) with the agent's formulated request. The output of this execution will then be automatically fed back as context into the *next turn* of the LLM interaction with that agent.  
     * **Deny:** If you deny, ai\_rails\_backend.py prompts you for a "personal response" (e.g., "MCP not available," "refine request"). This human feedback will then be automatically fed back as context into the *next turn* of the LLM interaction, allowing the agent to course-correct.  
7. **ai\_rails\_backend.py (Mac Mini):** Logs the interaction and prompts the human for the next overall step (e.g., "review the plan," "engage Coder Agent").

#### **4\. Agent Bounding & Protocol**

To ensure agents stay on "rails" and prevent "gaming" the logs:

* **System Prompts are the Contract:** The verbose and explicit system prompts (.md files) are the primary mechanism for bounding agent behavior. They define the agent's persona, its exact process, allowed actions, and explicitly forbidden actions.  
* **Strict Input/Output (Script/UI Managed):**  
  * The ai\_rails\_backend.py script/UI is the gatekeeper. It explicitly defines *what* input is passed to the LLM and *where* its raw output is saved.  
  * The structure of input files (e.g., feature\_update\_idea.md) and command-line arguments are designed to feed agents exactly the context they need, no more, no less.  
* **Human Gating (Mandatory Review & Decision):** Each significant transition in the workflow requires explicit human approval (UI button click / script prompt). This is where you verify agent output, decide the next step, and **crucially, explicitly approve or deny agent requests for MCP queries or tool executions.**  
* **No Autonomous Tool Invocation:** This is critical. Agents *do not* directly execute n8n workflows or query MCP servers. Instead, their system prompts instruct them to *formulate a request* in their output. The script/UI *detects*, *presents*, and *executes* these requests only upon human approval. This breaks the direct "action" link from the AI.  
* **Centralized, Script-Controlled Logging:**  
  * **Dedicated Log File:** All workflow actions, human choices, and key agent inputs/outputs (or pointers to them) are recorded by the ai\_rails\_backend.py backend into a single, append-only log file (ai-rails.log within a log/ directory).  
  * **Human Control of Logs:** Because the logging mechanism is embedded within the *dumb* backend script, the LLMs themselves cannot modify or "game" the log file. They simply produce output that is then recorded.  
  * **Content:** The log will include: timestamps, user choices, paths to input files given to agents, indications of when an agent session started/ended, and summaries of expected outputs. *Full LLM outputs won't be in the log, but pointers to where they are saved in output/ will be.*

#### **5\. MCP Management & Access**

* **Purpose:** To provide dynamic, specialized context to agents (like highly specific codebase details, up-to-date API references, or detailed industry standards) and, in the future, enable *controlled, human-approved actions*. They act as specialized RAG endpoints and controlled action proxies.  
* **Deployment (on AI Workhorse \- 10.0.0.2):**  
  * Each MCP is a lightweight, independent microservice (e.g., a Python Flask/FastAPI app, often containerized with Docker).  
  * **Knowledge-Based MCPs:** Provide up-to-date, specialized information. Examples:  
    * MCP-Sequential-Thinking (e.g., from glama.ai): Provides structured reasoning and breakdown of tasks.  
    * Context7 (e.g., from Upstash/GitHub): Provides vector-database backed context retrieval for docs/memory.  
    * **CodebaseSummaryMCP (Custom):** A dedicated MCP for providing summarized or indexed information about your local codebase. This would be a service you run on the Workhorse, potentially indexing files from your NAS or synced directories.  
    * **SecretsMCP (Custom \- New):** A dedicated MCP for securely managing and serving environment variables and API keys to agents.  
  * **Action-Oriented MCPs (Future):** (e.g., "Database Change MCP", "File System Write MCP"). These would expose highly constrained APIs for controlled execution of specific, potentially impactful actions.  
  * **API Interface:** Exposed via HTTP over the 10 Gigabit Ethernet link (e.g., http://10.0.0.2:8001/query, http://10.0.0.2:8002/context, http://10.0.0.2:8003/code\_summary, http://10.0.0.2:8004/get\_secret).  
  * **Embedded Vector Database:** Used by Context7 and custom MCPs (like CodebaseSummaryMCP) for efficient context retrieval.  
* **Modular MCP Configuration (templates/mcp\_definitions/):**  
  * This dedicated subdirectory will store modular JSON definitions for each available MCP (e.g., codebase\_summary\_mcp.json, n8n\_automation\_mcp.json, secrets\_mcp.json).  
  * These JSON files will describe the MCP's mcp\_name, description, api\_endpoint, capabilities (available functions), request\_schema, and response\_format.  
  * **The UI/Backend will dynamically load these JSON definitions** and inject the relevant ones into the active agent's system prompt, telling the agent what tools are available and how to request them. This creates the "modular MCP config."  
* **Access by Agents (Formulated Request):**  
  * Agents are made aware of available MCPs by dynamic injection of their definitions into the agent's system prompt (managed by UI/backend).  
  * When an agent determines it needs specific context or wants to propose an action, it formulates an MCP query request within its output, specifying the mcp\_name and the query parameters according to the MCP's defined schema.  
* **Control/Execution (Human-gated with Future UI / ai\_rails\_backend.py):**  
  * **UI/Backend as Interceptor:** When an agent's output contains an MCP Query Request (or n8n Automation Request), the UI/backend will detect it.  
  * **Visual Alert & Approval:** The UI will present a prominent "alert" (e.g., a modal dialog) showing:  
    * Which agent is requesting the MCP/tool.  
    * The full "naked request" (the raw JSON formulated by the agent).  
    * A clear explanation of what the MCP/tool is expected to do.  
  * **Accept/Deny & Custom Response:**  
    * **Accept:** If you accept, the UI/backend triggers a backend execution (e.g., via call\_mcp.py for MCPs, or direct API call for n8n) with the agent's formulated request. The output of this execution will then be automatically fed back as context into the *next turn* of the LLM interaction with that agent.  
    * **Deny:** If you deny, the UI/backend prompts you for a "personal response" (e.g., "MCP not available," "refine request"). This human feedback will then be automatically fed back as context into the *next turn* of the LLM interaction, allowing the agent to course-correct.  
* **Gating Strategy for MCPs:**  
  * **Knowledge-Based MCPs (e.g., Context7, MCP-Sequential-Thinking, CodebaseSummaryMCP):** The primary "gate" is the human review of the *returned context* before it's fed to the LLM. The UI/backend will execute the query and display the results for your approval.  
  * **Action-Oriented MCPs (Future Feature):** For MCPs that *enable actions* (e.g., a "Database Change MCP" that could modify your database), the gating will be stricter. The agent will formulate the *exact action request*. The UI would then prompt you to *review this action request extremely carefully* before providing a final, explicit confirmation to a specialized backend script that executes it. This script would log the action extensively.  
* **SecretsMCP (Universal .env):**  
  * **Mechanism:** The SecretsMCP will manage your API keys and environment variables. It will expose a controlled API (e.g., http://10.0.0.2:8004/get\_secret?name=\<VAR\_NAME\>).  
  * **Agent Awareness:** Agents will be told about SecretsMCP in their prompts and instructed on which variable names they can request.  
  * **Permissioned Access:**  
    * **"Free Agentic Access" (for less sensitive variables):** The SecretsMCP's API could be configured to return certain variables immediately upon request from *any* agent, without human intervention (e.g., DEFAULT\_N8N\_WEBHOOK\_URL). These variables would be listed in the prompt as "freely available."  
    * **"Permissioned Access" (for sensitive keys):** For keys like ANTHROPIC\_API\_KEY or DB\_PASSWORD, when an agent requests them via SecretsMCP, the UI/backend will *intercept* this request. It will trigger a human approval prompt, displaying the secret name and the requesting agent. Only upon your explicit approval will the UI/backend retrieve the secret from SecretsMCP and inject it into the LLM's context (e.g., as part of the OLLAMA\_API\_KEY or CLAUDE\_API\_KEY environment variable for the LLM client call). This is critical for security.  
  * **File Hiding:** The actual .env file containing the secrets will reside *only* on the Workhorse (or NAS) and will *not* be accessible by the LLM client on the Mac Mini, nor directly by the LLMs themselves. The SecretsMCP is the sole gateway.

#### **6\. LLM Prioritization (Qwen vs. Claude Fallback)**

* **Default Local Model (qwen2.5-coder:32b via Ollama):** For most coding, testing, and debugging tasks, your powerful local model will be the default.  
  * **ai\_rails\_backend.py / UI Instruction:** The backend will explicitly configure and make the API calls to your Ollama server on your Workhorse (http://10.0.0.2:11434), running Qwen2.5-coder:32b.  
  * **Agent System Prompt Adaptation:** Coder, Unit Tester, Debugger, and Refactor Agent system prompts will be updated to imply they are operating as a highly capable *local* coding model. They will be directed to be concise and code-focused, as Qwen excels here.  
* **Claude as Strategic Fallback (Claude 4 Opus via Claude Code):** Reserved for:  
  * **"Very large and hairy problems":** When Qwen struggles, hallucinates badly, or when a task requires extremely high-level reasoning or extensive new research not covered by an MCP, or complex, nuanced problem-solving.  
  * **Review and Backup:** The Code Review Agent could potentially default to Claude for higher-fidelity review of critical code, or you might explicitly choose Claude for such tasks.  
* **Managed by UI / ai\_rails\_backend.py (Human Choice & Automated Fallback):**  
  * When you select an action (e.g., "Engage Coder Agent"), the UI/backend will present a clear choice: "Use Local Qwen (default)" or "Use Claude (fallback for hairy problems)."  
  * Based on your choice, the backend will then make the appropriate API calls to the selected LLM.  
  * **Automated Retry & Fallback (New):**  
    * The backend will track "retries" for an agent's task. If an agent fails to produce a satisfactory output (as determined by your manual acceptance or rejection) after a configurable number of attempts (e.g., 3 retries):  
      1. The backend will automatically trigger a **Brave Search/Stack Overflow MCP query** (assuming such an MCP is implemented). It will formulate a search query based on the last input/problem, execute it via the MCP, and feed the *search results* back to the agent for another attempt.  
      2. If the agent *still* fails after another configurable number of attempts (e.g., 1-2 attempts after search context), the UI/backend will explicitly **suggest switching to Claude** and ask for your human confirmation.  
      3. If the problem persists with Claude, it will trigger a "Manual Intervention Required" alert, suggesting direct human review or intervention, potentially providing all relevant logs and outputs.  
    * **Implementation Effort:** Tracking retries and conditional logic in Python is straightforward. Integrating a Brave Search MCP requires developing that specific MCP (or finding an existing one) and writing the call\_mcp.py logic for it. The effort for this automated retry/fallback is moderate but highly valuable. The ability to switch LLMs mid-session is *not* planned for MVP; rather, the *session* restarts with the new LLM if you choose to switch.

---

### **7\. Secure Secrets Management (SecretsMCP)**

The `SecretsMCP` is a critical component for securely managing and serving sensitive environment variables and API keys to AI agents while strictly adhering to the human-in-the-loop and least-privilege principles. It centralizes secrets, prevents their exposure in code or logs, and enables fine-grained human approval for sensitive access.

#### **Architecture & Flow:**

1.  **Dedicated SecretsMCP Service (AI Workhorse):**
    * A lightweight Python FastAPI service is deployed on the AI Workhorse (e.g., at `http://10.0.0.2:8004`), in its own dedicated Git repository (`secrets-mcp/`).
    * This service reads sensitive secrets from its *own, highly-secured `.env` file* (e.g., `/opt/secrets_mcp/.env`) with strict file permissions (e.g., `chmod 600`). This `.env` file is never committed to Git.
    * It exposes a `/get_secret` endpoint.
    * **Authentication:** The service implements authentication middleware (e.g., using an `X-API-Key` header) to ensure only authorized clients can request secrets. This `SECRETS_MCP_AUTH_KEY` is stored securely in the SecretsMCP's `.env`.
    * Logging is implemented for audit trails of secret requests.

2.  **AI Rails Backend Client (Mac Mini):**
    * The `ai_rails_backend.py` script on the Mac Mini is the client that initiates secret requests via `call_mcp.py`.
    * It has its own non-sensitive `.env` file (`.ai-rails/.env`) which contains the `SecretsMCP` URL and the `AI_RAILS_SECRETS_MCP_AUTH_TOKEN` (the authentication token for the `SecretsMCP` service).
    * When an agent requests a secret:
        * `ai_rails_backend.py` checks if the requested `secret_name` is in a predefined `SENSITIVE_SECRETS` list (e.g., `["ANTHROPIC_API_KEY", "DB_PASSWORD"]`).
        * If it's a sensitive secret, `ai_rails_backend.py` **pauses** and prompts the human operator for explicit approval.
        * If approved (or if the secret is not sensitive), `call_mcp.py` is invoked.

3.  **`call_mcp.py` (The Dispatcher):**
    * Retrieves the `AI_RAILS_SECRETS_MCP_AUTH_TOKEN` from its environment.
    * Makes an authenticated HTTP POST request to the `SecretsMCP`'s `/get_secret` endpoint, including the `secret_name` in the payload and the authentication token in the headers.

4.  **Secure Secret Transmission:**
    * The `SecretsMCP` retrieves the requested secret from its secure `.env` file.
    * It returns the actual secret value securely over the 10GbE link to `call_mcp.py`.
    * `ai_rails_backend.py` receives the secret value and temporarily injects it into the LLM's context for that specific turn, or makes it available for a tool execution, **without persisting it or exposing it to the agent directly in its prompt history.**

#### **Security Measures:**

* **Isolation:** Sensitive secrets are isolated to the Workhorse/NAS, never residing directly on the Mac Mini in a committable file.
* **Human Gating:** Explicit human approval acts as a circuit breaker for all sensitive secret requests.
* **Authentication:** Client-to-service authentication prevents unauthorized access to the `SecretsMCP`.
* **Least Privilege:** SecretsMCP only exposes the requested secret, not the entire `.env` file.
* **Auditing:** Logging of secret requests provides an audit trail.
* **Containerization:** Deploying SecretsMCP as a Docker container ensures isolation and repeatable deployment.

---

### **8. Simple UI/Dashboard (App-like Web Controller - MVP Priority)**

The AI Rails UI will provide a clean, web-based interface to replace the command-line `run_workflow.sh` script, making the system more accessible and user-friendly while maintaining the core principle of human control.

#### **Architecture & Technology Stack:**

1. **Backend (Python FastAPI):**
   * FastAPI service running on the Mac Mini alongside `ai_rails_backend.py`
   * Manages workflow state, agent orchestration, and MCP/tool requests
   * WebSocket support for real-time agent output streaming
   * RESTful API endpoints for workflow control
   * Session management for concurrent projects

2. **Frontend (React/Next.js):**
   * Modern, responsive single-page application
   * Real-time updates via WebSocket connections
   * Clean, terminal-inspired design with better UX
   * Modal dialogs for MCP/tool approval workflows
   * Syntax highlighting for code outputs

3. **Key Features:**
   * **Project Dashboard:** Overview of all active and past projects
   * **Workflow Wizard:** Guided flow for new projects, feature updates, and takeovers
   * **Agent Monitor:** Real-time view of agent activities with streaming outputs
   * **Approval Interface:** Clear, prominent alerts for MCP/tool requests with:
     - Visual indication of request type and severity
     - Formatted display of request parameters
     - Accept/Deny buttons with optional feedback
   * **Output Viewer:** In-browser viewing of agent outputs with syntax highlighting
   * **Log Explorer:** Searchable, filterable view of the ai-rails.log
   * **LLM Selector:** Easy switching between Ollama and Claude with status indicators

4. **Implementation Plan:**
   * Phase 1: Basic workflow control (start, stop, select agents)
   * Phase 2: Real-time output streaming and approval dialogs
   * Phase 3: Enhanced features (search, filtering, project management)

This UI will significantly improve the user experience while maintaining the strict human-in-the-loop control that is fundamental to the AI Rails philosophy.