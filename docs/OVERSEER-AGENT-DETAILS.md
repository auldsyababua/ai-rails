# Overseer Agent: Detailed Design & Integration

## 1. Philosophy & Role

The Overseer Agent is a critical component of the AI Rails system, designed to enhance safety, transparency, and efficiency through passive, intelligent monitoring. It embodies the "two sets of eyes" principle, providing an independent, objective perspective on the ongoing AI-human workflow.

* **Passive Observer:** The Overseer Agent *never* directly controls the workflow or communicates with other agents. Its sole function is to observe the `ai-rails.log` and report anomalies to the human operator. This maintains the "dumb orchestrator" philosophy.
* **Anomaly Detection:** It acts as an automated "red team" or a vigilant assistant, identifying deviations from plan, potential hallucinations, inefficiencies, or unexpected behavior from the working agents.
* **Independent Perspective:** By typically running on a different (and potentially higher-capability) LLM model (e.g., Claude Opus if Qwen is the primary coding model), it offers a fresh, unbiased analytical lens.
* **Human-Gated Intervention:** All its findings are presented to the human operator for review and decision, ensuring human oversight remains the ultimate control point.

## 2. Architectural Integration

The Overseer Agent is implemented as a separate, continuously running Python daemon (`overseer_daemon.py`), communicating with the main `ai_rails_backend.py` (and eventually the UI) via a controlled channel.

+-----------------+       +-----------------------+        +--------------------------+
|  ai_rails_backend.py  |       |  ai-rails.log (JSONL) |        |  overseer_daemon.py      |
|  (Main Workflow Logic)  | ----> | (Append-Only Log File) | <----  | (Overseer Logic)         |
+-----------------+       +-----------------------+        +--------------------------+
^                                                               |
|                                                               | Alerts (e.g., WebSocket / HTTP Push)
| (Human Actions/Responses)                                     v
+------------------------------------------------------------------------------------------+
|                                    AI Rails UI (Web-based)                               |
|                                                                                          |
| +---------------------+   +-----------------------+   +-------------------------------+|
| |  Output Box         |   |  Agent Interaction    |   |  Real-time Log Viewer         ||
| | (Rendered Markdown) |   |  (Current Input/Output) |   |                               ||
| +---------------------+   +-----------------------+   +-------------------------------+|
|                                                                                          |
|                          +-------------------------------------------------------------+ |
|                          |     OVERSEER ALERT (Prominent Modal/Notification)           | |
|                          |     -------------------------------------                   | |
|                          |     Agent: [Agent Role]                                 | |
|                          |     Problem: [Brief Anomaly Description]                | |
|                          |     Log ID: [Timestamp/ID of problematic entry]         | |
|                          |     Full Request: [Raw JSON of agent's suspicious request]|
|                          |     Explanation: [Why Overseer flagged this]            | |
|                          |     Suggested Prompt: [Prompt for working agent]        | |
|                          |                                                             | |
|                          |     [ Big Red "Accept & Run Suggested Prompt" Button ]      | |
|                          |     [ "Deny & Send Custom Feedback" Button ]                | |
|                          |     [ "Deny & Stop Agent" Button ]                          | |
|                          +-------------------------------------------------------------+ |
+------------------------------------------------------------------------------------------+

## 3. Log Monitoring & Anomaly Detection Strategy

The effectiveness of the Overseer hinges on a robust log structure and intelligent anomaly detection.

* **Structured Logging (`ai-rails.log`):**
    * All interactions are logged in a structured format (preferably [JSONL](https://jsonlines.org/)). This allows `overseer_daemon.py` to easily parse entries.
    * Each log entry will include: `timestamp`, `session_id`, `agent_role`, `llm_model_used`, `event_type` (e.g., `AGENT_PROMPT_SENT`, `AGENT_RESPONSE_RECEIVED`, `MCP_REQUEST_FORMULATED`, `HUMAN_FEEDBACK`), `content_summary`, and pointers to full content in `output/` if applicable. For `MCP_REQUEST_FORMULATED`, the full JSON request will be embedded.

* **Overseer's Context Management (Summarization Strategy):**
    * The `overseer_daemon.py` will read new log entries and send them to the Overseer LLM.
    * To manage context window limits, the Overseer LLM's system prompt will instruct it to:
        1.  **Summarize past interactions:** Periodically, or after a certain number of turns/tokens, the Overseer LLM will summarize the key developments and its ongoing "mental state" about a session. This summary is then used in subsequent prompts to the Overseer itself.
        2.  **Focus on deltas:** Primarily analyze the *newest* log entries in the context of its summarized understanding.
    * This "sliding window + summarization" approach ensures the Overseer always has the most relevant context without bloating its prompt.

* **Anomaly Detection Logic (Within Overseer System Prompt):**
    * The `overseer_agent_system_prompt.md` (defined previously) will contain detailed instructions on what constitutes an anomaly. This includes looking for:
        * Repetitive patterns in agent output.
        * Syntax errors in generated code after a "Coder Agent" turn.
        * Tool requests that don't align with the current phase or explicit instructions.
        * Unusually short or generic answers when detail is expected.
        * Hallucinations (requiring the Overseer to perform basic sanity checks or flag suspicious claims).
        * Stalling behavior (e.g., multiple log entries with minimal progress).

## 4. Interruption Mechanism & Human Response

When `overseer_daemon.py` receives an anomalous response from the Overseer LLM, it triggers an alert in the UI.

* **Visual Alert (UI):** A prominent, non-dismissible (until actioned) modal dialog or notification will appear, displaying:
    * The **requesting agent** (e.g., "Coder Agent")
    * The **problem description** (from the Overseer's output)
    * The **relevant `log_id`** for easy lookup
    * The **full "naked request"** from the working agent that triggered the anomaly (if applicable, e.g., an suspicious MCP query)
    * The Overseer's **suggested `interruption_prompt`** (e.g., "Review your last response for correctness and adherence to the plan. I believe there's a logical error in the loop on line 15.")

* **Human Action Buttons:**
    * **"Accept & Run Suggested Prompt":** Sends the Overseer's suggested `interruption_prompt` directly to the working agent via `ai_rails_backend.py`. This immediately feeds back the corrective context to the original agent.
    * **"Deny & Send Custom Feedback":** Opens an input box for the human operator to type their own response to the working agent (e.g., "Disregard Overseer, please continue as planned, I understand the current output."). This response is then sent to the working agent.
    * **"Deny & Stop Agent":** Terminates the current agent session and returns control to the overall workflow selection. This is for unrecoverable situations or when the human wants to take over manually.

## 5. LLM Model for Overseer

* The Overseer Agent will typically run on a different LLM model than the primary working agent (Qwen2.5-coder:32b).
* **Recommended:** Claude 4 Opus (via Claude Code CLI or API) is a strong candidate for the Overseer due to its high reasoning capabilities, detailed explanations, and strong performance in anomaly detection. This provides a truly "fresh pair of eyes" compared to the local Qwen model.
* `ai_rails_backend.py` will manage the API calls to this separate LLM instance for the Overseer.

This detailed plan for the Overseer Agent ensures robust monitoring and controlled intervention, reinforcing the safety and precision of your "AI Rails" system.


Gemini can make mistakes, so double-check it
AI Rails: A Human-Centric, Bounded AI Engineering Workflow (High-Level Design)
AI Rails: A Human-Centric, Bounded AI Engineering Workflow

Version: 1.4

Date: June 19, 2025

Author: Gemini (with user collaboration)
1. Philosophy & Core Principles

The "AI Rails" architecture is designed for high-performance, precise, and auditable AI-assisted software development. It prioritizes human control, transparency, and safety by adopting a "dumb orchestrator" model and strictly bounding AI agent capabilities.

    Human-as-Orchestrator (You): The ultimate decision-maker, director, and quality gate. All critical decisions and transitions between phases are human-gated.

    Dumb Orchestrator Script (run_workflow.sh / Future UI Backend): This core component is a purely rule-based state machine at the workflow decision level. It contains zero AI decision-making. Its sole purpose is to guide the human operator, presenting choices, dictating input/output paths, defining the sequence of operations, and programmatically interacting with LLMs and tools. This prevents any single AI from accumulating "god mode" control over the workflow itself.

        Implementation Language: The core backend orchestration and UI logic will primarily be built using Python due to its maintainability and proficiency of LLMs in writing it. The run_workflow.sh script will evolve into a bootstrap/orchestrator for these Python components.

    Bounded & Compartmentalized Agents (AI on Rails): Each AI agent (e.g., Planner, Coder, Tester, Overseer) is defined by a rigid system prompt (.md file in templates/). These prompts act as strict "rails," confining the AI's intelligence to a specific domain (e.g., planning, coding, testing, anomaly detection) and preventing it from hallucinating beyond its defined role, making autonomous workflow decisions, or engaging in unauthorized actions.

    Explicit Human-in-the-Loop: Mandatory human review and approval checkpoints are built into the workflow. This serves as a vital circuit breaker against unintended AI behavior, mesa-optimization, and ensures human "taste" and expertise are central. This includes explicit human approval for agent-requested MCP queries or tool executions, and for responding to Overseer Agent alerts.

    File-Based Communication Protocol: All communication between different workflow stages and agents is mediated by structured files (Markdown, JSON) saved to disk. An agent's output is saved to a file, reviewed by the human, and then becomes the explicit input for the next stage or agent. This provides transparency and debuggability.

    Transparency & Auditability (Logging): All significant interactions, inputs, and outputs within the workflow are logged to a dedicated, human-readable file, managed solely by the run_workflow.sh script/UI backend. This prevents agents from "gaming" their own logs, providing an objective record of their actions and outputs.

    Compounding Engineering: The architecture promotes the continuous improvement of templates, prompts, and the guiding script itself, making future development efforts more efficient and reliable.

    Hybrid LLM Strategy: Leverages powerful local LLMs (Qwen2.5-coder:32b) for default operation and utilizes more capable but potentially costlier remote LLMs (Claude Opus) as a strategic fallback for complex or "hairy" problems. The Overseer Agent will typically run on a different, potentially higher-capability, model to provide a fresh perspective.

2. Architectural Components

The system is distributed across your Mac Mini (control plane) and AI Workhorse (inference & services).

    Human Operator (You):

        Role: The ultimate orchestrator, decision-maker, and quality gate. You interact with the run_workflow.sh script/UI, review agent outputs, and approve/deny agent-initiated actions or context requests. You also respond to alerts from the Overseer Agent.

        Device: Mac Mini M4 (192.168.1.209 / 10.0.0.1)

    AI Rails Repository (~/Desktop/projects/ai-engineering-workflow/ on Mac Mini):

        run_workflow.sh: The initial "Dumb Orchestrator" script. This will bootstrap and orchestrate Python backend scripts.

        ai_rails_backend.py (New): The primary Python script handling LLM API calls, output parsing, log management, and interaction with MCPs/tools. This backend will also communicate with the Overseer Agent.

        templates/: Stores all bounded AI agent system prompts (e.g., planning_agent_system_prompt.md, coder_agent_system_prompt.md), initial kickoff templates (new_project_kickoff_template.md, feature_update_kickoff_template.md, takeover_project_kickoff_template.md), and external tool definitions.

        templates/mcp_definitions/: Stores modular JSON definitions for each available MCP, to be dynamically injected into agent prompts by the backend.

        output/: Directory for storing all generated outputs (plans, code snippets, test reports, debug logs, review reports) from AI agent interactions.

        log/: A dedicated directory for ai-rails.log which records all script actions and key human-AI interactions.

    AI Agent Clients (Managed Programmatically by ai_rails_backend.py / UI Backend):

        Local LLM Interaction: ai_rails_backend.py will make direct API calls to your Ollama server on the Workhorse for Qwen2.5-coder:32b.

        Remote LLM Interaction: ai_rails_backend.py will use a Python client for Claude 4 Opus (either directly via API or by programmatically interacting with Claude Code CLI if direct API is not preferred for specific reasons).

    AI Workhorse (10.0.0.2 - 192.168.1.199):

        Local LLM Inference Engine:

            Ollama Server: Hosts and serves your qwen2.5-coder:32b and other local models. Accessible via network (e.g., http://10.0.0.2:11434).

        Dynamic MCP Server Layer (Existing & Custom Implementations):

            MCP Servers: Independent, specialized microservices running on the Workhorse, offering specific contextual data or limited, controlled actions.

            Knowledge-Based MCPs: Provide up-to-date, specialized information. Examples:

                MCP-Sequential-Thinking (e.g., from glama.ai): Provides structured reasoning and breakdown of tasks.

                Context7 (e.g., from Upstash/GitHub): Provides vector-database backed context retrieval for docs/memory.

                CodebaseSummaryMCP (Custom): A dedicated MCP for providing summarized or indexed information about your local codebase. This would be a service you run on the Workhorse, potentially indexing files from your NAS or synced directories.

                SecretsMCP (Custom): A dedicated MCP for securely managing and serving environment variables and API keys to agents.

            Action-Oriented MCPs (Future): (e.g., "Database Change MCP", "File System Write MCP"). These would expose highly constrained APIs for controlled execution of specific, potentially impactful actions.

            API Interface: Exposed via HTTP (e.g., http://10.0.0.2:8001/query, http://10.0.0.2:8002/context, http://10.0.0.2:8003/code_summary, http://10.0.0.2:8004/get_secret).

            Embedded Vector Database: Used by Context7 and custom MCPs for efficient context retrieval.

        n8n Automation Engine: Your self-hosted n8n instance, accessible over the network (e.g., http://192.168.1.3:80/n8n via Nginx Proxy).

3. Communication & Control Flow

+----------------+      +--------------------+      +---------------------------------+
|   Human        |<-----|  AI Rails Repo     |<---->|         AI Workhorse            |
| (Mac Mini)     |      |  (Mac Mini)        |      | (10.0.0.2 / 192.168.1.199)      |
|                |      |                    |      |                                 |
|  - Reviews     |      | - `run_workflow.sh`|      |  - Ollama Server (Qwen:32b)     |
|  - Approves/   |      |    (Dumb Orchestrator)    |  - MCP Servers (e.g., :8001, :8002) |
|    Denies      |      | - `templates/`     |      |  - N8n Automation Engine        |
|                |      | - `output/`        |      |    (via NAS/Nginx)              |
|                |      | - `log/`           |      |  - Embedded Vector DBs (for MCPs)|
|                |      +---------^----------+      +---------------------------------+
|                |                |
|                |                | Orchestrates
|                |                | LLM/Tool Calls
+------^---------+                |
       |                          |
       |  Automated Prompt/Input Passing
       |  Automated Output Capture
       |
+------v------------------------------------+
|  LLM Client Interaction (Programmatic)   |
|                                            |
|  - **Default:** Ollama API Calls (to       |
|    Workhorse:11434 for Qwen:32b)           |
|  - **Fallback:** Claude API Calls (to      |
|    Anthropic API via `claude` CLI)         |
+--------------------------------------------+

Workflow Summary:

    run_workflow.sh (Mac Mini): Initiates the workflow. It can accept command-line arguments (e.g., airails new-project my-app "Create a mobile app for X") to bypass interactive prompts, or guide the human through choices.

    Human (Mac Mini) / run_workflow.sh: Provides custom inputs (project name, initial summary, etc.). For templates with blanks, the script/UI will ask the human to write and enter the content.

    ai_rails_backend.py (Mac Mini):

        Reads the relevant Agent System Prompt from templates/.

        Reads the task-specific input (from files or command-line args).

        Dynamically loads MCP definitions (from templates/mcp_definitions/) and injects relevant portions into the LLM's system prompt.

        Makes a programmatic API call to the chosen LLM (Ollama on Workhorse or Claude).

    AI Agent (Qwen/Claude): Processes the prompt, generates output (plan, code, review, etc.) according to its bounded system prompt. If the agent formulates an MCP query or tool request (e.g., MCP Query Request, n8n Automation Request), this is embedded within its output.

    ai_rails_backend.py (Mac Mini):

        Captures the AI's output directly.

        Saves the AI's output to a designated file in the output/ directory.

        Detects any embedded MCP Query Request or n8n Automation Request within the AI's output.

    Human Gating for Agent Requests (Future UI / ai_rails_backend.py):

        If an MCP/tool request is detected, the UI (or ai_rails_backend.py in terminal mode) will pause and present a clear "alert" to the human:

            Which agent made the request.

            The full "naked request" (the raw JSON formulated by the agent).

            A clear explanation of what the MCP/tool is expected to do.

        Accept/Deny Options:

            Accept: If you accept, ai_rails_backend.py triggers a backend execution (e.g., via call_mcp.py for MCPs, or direct API call for n8n) with the agent's formulated request. The output of this execution will then be automatically fed back as context into the next turn of the LLM interaction with that agent.

            Deny: If you deny, ai_rails_backend.py prompts you for a "personal response" (e.g., "MCP not available," "refine request"). This human feedback will then be automatically fed back as context into the next turn of the LLM interaction, allowing the agent to course-correct.

    ai_rails_backend.py (Mac Mini): Logs the interaction and prompts the human for the next overall step (e.g., "review the plan," "engage Coder Agent").

4. Agent Bounding & Protocol

To ensure agents stay on "rails" and prevent "gaming" the logs:

    System Prompts are the Contract: The verbose and explicit system prompts (.md files) are the primary mechanism for bounding agent behavior. They define the agent's persona, its exact process, allowed actions, and explicitly forbidden actions.

    Strict Input/Output (Script/UI Managed):

        The ai_rails_backend.py script/UI is the gatekeeper. It explicitly defines what input is passed to the LLM and where its raw output is saved.

        The structure of input files (e.g., feature_update_idea.md) and command-line arguments are designed to feed agents exactly the context they need, no more, no less.

    Human Gating (Mandatory Review & Decision): Each significant transition in the workflow requires explicit human approval (UI button click / script prompt). This is where you verify agent output, decide the next step, and crucially, explicitly approve or deny agent requests for MCP queries or tool executions.

    No Autonomous Tool Invocation: This is critical. Agents do not directly execute n8n workflows or query MCP servers. Instead, their system prompts instruct them to formulate a request in their output. The script/UI detects, presents, and executes these requests only upon human approval. This breaks the direct "action" link from the AI.

    Centralized, Script-Controlled Logging:

        Dedicated Log File: All workflow actions, human choices, and key agent inputs/outputs (or pointers to them) are recorded by the ai_rails_backend.py backend into a single, append-only log file (ai-rails.log within a log/ directory).

        Human Control of Logs: Because the logging mechanism is embedded within the dumb backend script, the LLMs themselves cannot modify or "game" the log file. They simply produce output that is then recorded.

        Content: The log will include: timestamps, user choices, paths to input files given to agents, indications of when an agent session started/ended, and summaries of expected outputs. Full LLM outputs won't be in the log, but pointers to where they are saved in output/ will be.

5. MCP Management & Access

    Purpose: To provide dynamic, specialized context to agents (like highly specific codebase details, up-to-date API references, or detailed industry standards) and, in the future, enable controlled, human-approved actions. They act as specialized RAG endpoints and controlled action proxies.

    Deployment (on AI Workhorse - 10.0.0.2):

        Each MCP is a lightweight, independent microservice (e.g., a Python Flask/FastAPI app, often containerized with Docker).

        Knowledge-Based MCPs: Provide up-to-date, specialized information. Examples:

            MCP-Sequential-Thinking (e.g., from glama.ai): Provides structured reasoning and breakdown of tasks.

            Context7 (e.g., from Upstash/GitHub): Provides vector-database backed context retrieval for docs/memory.

            CodebaseSummaryMCP (Custom): A dedicated MCP for providing summarized or indexed information about your local codebase. This would be a service you run on the Workhorse, potentially indexing files from your NAS or synced directories.

            SecretsMCP (Custom - New): A dedicated MCP for securely managing and serving environment variables and API keys to agents.

        Action-Oriented MCPs (Future): (e.g., "Database Change MCP", "File System Write MCP"). These would expose highly constrained APIs for controlled execution of specific, potentially impactful actions.

        API Interface: Exposed via HTTP over the 10 Gigabit Ethernet link (e.g., http://10.0.0.2:8001/query, http://10.0.0.2:8002/context, http://10.0.0.2:8003/code_summary, http://10.0.0.2:8004/get_secret).

        Embedded Vector Database: Used by Context7 and custom MCPs (like CodebaseSummaryMCP) for efficient context retrieval.

    Modular MCP Configuration (templates/mcp_definitions/):

        This dedicated subdirectory will store modular JSON definitions for each available MCP (e.g., codebase_summary_mcp.json, n8n_automation_mcp.json, secrets_mcp.json).

        These JSON files will describe the MCP's mcp_name, description, api_endpoint, capabilities (available functions), request_schema, and response_format.

        The UI/Backend will dynamically load these JSON definitions and inject the relevant ones into the active agent's system prompt, telling the agent what tools are available and how to request them. This creates the "modular MCP config."

    Access by Agents (Formulated Request):

        Agents are made aware of available MCPs by dynamic injection of their definitions into the agent's system prompt (managed by UI/backend).

        When an agent determines it needs specific context or wants to propose an action, it formulates an MCP query request within its output, specifying the mcp_name and the query parameters according to the MCP's defined schema.

    Control/Execution (Human-gated with Future UI / ai_rails_backend.py):

        UI/Backend as Interceptor: When an agent's output contains an MCP Query Request (or n8n Automation Request), the UI/backend will detect it.

        Visual Alert & Approval: The UI will present a prominent "alert" (e.g., a modal dialog) showing:

            Which agent is requesting the MCP/tool.

            The full "naked request" (the raw JSON formulated by the agent).

            A clear explanation of what the MCP/tool is expected to do.

        Accept/Deny & Custom Response:

            Accept: If you accept, the UI/backend triggers a backend execution (e.g., via call_mcp.py for MCPs, or direct API call for n8n) with the agent's formulated request. The output of this execution will then be automatically fed back as context into the next turn of the LLM interaction with that agent.

            Deny: If you deny, the UI/backend prompts you for a "personal response" (e.g., "MCP not available," "refine request"). This human feedback will then be automatically fed back as context into the next turn of the LLM interaction, allowing the agent to course-correct.

    Gating Strategy for MCPs:

        Knowledge-Based MCPs (e.g., Context7, MCP-Sequential-Thinking, CodebaseSummaryMCP): The primary "gate" is the human review of the returned context before it's fed to the LLM. The UI/backend will execute the query and display the results for your approval.

        Action-Oriented MCPs (Future Feature): For MCPs that enable actions (e.g., a "Database Change MCP" that could modify your database), the gating will be stricter. The agent will formulate the exact action request. The UI would then prompt you to review this action request extremely carefully before providing a final, explicit confirmation to a specialized backend script that executes it. This script would log the action extensively.

    SecretsMCP (Universal .env):

        Mechanism: The SecretsMCP will manage your API keys and environment variables. It will expose a controlled API (e.g., http://10.0.0.2:8004/get_secret?name=<VAR_NAME>).

        Agent Awareness: Agents will be told about SecretsMCP in their prompts and instructed on which variable names they can request.

        Permissioned Access:

            "Free Agentic Access" (for less sensitive variables): The SecretsMCP's API could be configured to return certain variables immediately upon request from any agent, without human intervention (e.g., DEFAULT_N8N_WEBHOOK_URL). These variables would be listed in the prompt as "freely available."

            "Permissioned Access" (for sensitive keys): For keys like ANTHROPIC_API_KEY or DB_PASSWORD, when an agent requests them via SecretsMCP, the UI/backend will intercept this request. It will trigger a human approval prompt, displaying the secret name and the requesting agent. Only upon your explicit approval will the UI/backend retrieve the secret from SecretsMCP and inject it into the LLM's context (e.g., as part of the OLLAMA_API_KEY or CLAUDE_API_KEY environment variable for the LLM client call). This is critical for security.

        File Hiding: The actual .env file containing the secrets will reside only on the Workhorse (or NAS) and will not be accessible by the LLM client on the Mac Mini, nor directly by the LLMs themselves. The SecretsMCP is the sole gateway.

6. LLM Prioritization (Qwen vs. Claude Fallback)

    Default Local Model (qwen2.5-coder:32b via Ollama): For most coding, testing, and debugging tasks, your powerful local model will be the default.

        ai_rails_backend.py / UI Instruction: The backend will explicitly configure and make the API calls to your Ollama server on your Workhorse (http://10.0.0.2:11434), running Qwen2.5-coder:32b.

        Agent System Prompt Adaptation: Coder, Unit Tester, Debugger, and Refactor Agent system prompts will be updated to imply they are operating as a highly capable local coding model. They will be directed to be concise and code-focused, as Qwen excels here.

    Claude as Strategic Fallback (Claude 4 Opus via Claude Code): Reserved for:

        "Very large and hairy problems": When Qwen struggles, hallucinates badly, or when a task requires extremely high-level reasoning or extensive new research not covered by an MCP, or complex, nuanced problem-solving.

        Review and Backup: The Code Review Agent could potentially default to Claude for higher-fidelity review of critical code, or you might explicitly choose Claude for such tasks.

    Managed by UI / ai_rails_backend.py (Human Choice & Automated Fallback):

        When you select an action (e.g., "Engage Coder Agent"), the UI/backend will present a clear choice: "Use Local Qwen (default)" or "Use Claude (fallback for hairy problems)."

        Based on your choice, the backend will then make the appropriate API calls to the selected LLM.

        Automated Retry & Fallback (New):

            The backend will track "retries" for an agent's task. If an agent fails to produce a satisfactory output (as determined by your manual acceptance or rejection) after a configurable number of attempts (e.g., 3 retries):

                The backend will automatically trigger a Brave Search/Stack Overflow MCP query (assuming such an MCP is implemented). It will formulate a search query based on the last input/problem, execute it via the MCP, and feed the search results back to the agent for another attempt.

                If the agent still fails after another configurable number of attempts (e.g., 1-2 attempts after search context), the UI/backend will explicitly suggest switching to Claude and ask for your human confirmation.

                If the problem persists with Claude, it will trigger a "Manual Intervention Required" alert, suggesting direct human review or intervention, potentially providing all relevant logs and outputs.

            Implementation Effort: Tracking retries and conditional logic in Python is straightforward. Integrating a Brave Search MCP requires developing that specific MCP (or finding an existing one) and writing the call_mcp.py logic for it. The effort for this automated retry/fallback is moderate but highly valuable. The ability to switch LLMs mid-session is not planned for MVP; rather, the session restarts with the new LLM if you choose to switch.

7. Future Updates / Scratchpad

This section serves as a living document for potential improvements and ideas.

    Simple UI / Dashboard (App-like Web Controller - MVP Priority):

        Goal: A beautiful, simple, app-like experience to manage the "AI Rails" workflow, eliminating manual copy-pasting. This is an MVP feature.

        Technology: A Python web application (e.g., Flask, FastAPI with a lightweight frontend framework like HTMX, Alpine.js, or vanilla JS) running in a Docker container on your NAS (192.168.1.21) or Workhorse (10.0.0.2), accessible via your Nginx Proxy (192.168.1.3). This avoids Mac Mini localhost issues and centralizes UI hosting.

        Features:

            Output Box: Display the output from the previous step clearly, rendered as Markdown if applicable.

            "Send to Next Agent" Buttons: Automate the copy-pasting of current output as input to the next agent.

            Tool Use Automation: Buttons within the UI that, when clicked, trigger the execution of formulated MCP Query Requests or n8n Automation Requests via backend Python scripts. This eliminates manual copy-pasting for tools.

            Diff Viewer: An area to view code changes, diffs, and review reports.

            Commit/Push Integration: Buttons to trigger git commit and git push after code generation/review.

            Log Viewer: A dedicated panel to display the ai-rails.log in real-time, perhaps with filtering.

            Template Manager: A UI to view, edit, and manage agent system prompts and kickoff templates.

            Agent Request Alert System (New):

                When an MCP Query Request or n8n Automation Request is detected, a prominent UI alert (modal/notification) appears.

                Displays: Requesting Agent (Planner, Coder, etc.), full raw JSON request, explanation of the MCP/tool.

                Buttons: "Accept & Run Tool" (automates execution and feeds result to agent), "Deny & Send Custom Feedback" (opens input for human response to agent), "Deny & Stop Agent" (terminates current agent session).

    Command-Line Arguments / Quick Start Alias:

        Goal: Allow bypassing interactive prompts for common workflows using command-line arguments.

        Mechanism: Enhance run_workflow.sh to parse arguments like airails <alias_name> <project_location_or_name> <takeover_type> "<initial_summary>".

        Error Handling: If <project_location_or_name> is given for a "new project" command and the directory already exists, the script should reject with a message: "A project/directory with this name already exists. Please choose another name," then give a prompt for input of the new name (if interactive) or error out (if in non-interactive/alias mode). For "takeover" or "feature" modes, it would check for existence but not necessarily reject.

    Redis Support for Agent State Management:

        Goal: Maintain conversation history and short-term memory across multiple agent turns and sessions without constantly re-pasting large contexts.

        Mechanism: Utilize a Redis instance (on Workhorse or NAS).







open questions:

1. I normally give claude code wide latitutde to do what it wants and usually i like it this way, but not for this proejct. Can we create a separate claude.md file with greatly dimiinshed Create, Update, and Delete functions. The planner and reviewer dont need any of that. They only need to be abel to read and i am happy to give agents read abilities pretty unlimited.
2. we should have an n8n agent that creates the n8n flows specified and tehn i review them on the local n8n. Its much easier to review than to create and there is an n8n MCP that should make this stupid easy for the agent esepcially if they have context7 providing the latest versioned docs for that instance. 