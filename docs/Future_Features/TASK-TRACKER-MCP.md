# Future Feature - Agent Task Tracking and Learning System

## Overview

This design outlines an enhancement to the AI Rails system to introduce more robust task tracking and a simulated learning mechanism for agents. The goal is to enforce task completion, provide verifiable status updates, and enable agents to "learn" from past mistakes through structured feedback and system-level improvements. This moves beyond simple output generation to a more accountable and adaptable agent workflow.

## Core Principles

* **Human-Gated Accountability**: All critical task completion or status updates initiated by agents will require explicit human approval, preventing "lazy LLM" behavior.
* **Structured Feedback Loop**: Agents will receive detailed, actionable feedback when their outputs or tool requests are invalid or unsatisfactory, prompting self-correction within a session.
* **Compounding Engineering for System-Level Learning**: Repeated agent mistakes will trigger human-driven improvements to agent prompts, MCP schemas, or the addition of specialized tools, thereby "teaching" the system over time.
* **Verifiable Status**: Task updates will be logged and reflected in a centralized GUI for transparency and auditability.

## Architectural Components & Changes

### 1. New MCP: TaskTrackerMCP

This will be a custom-built MCP designed specifically for interacting with task management.

* **Purpose**: To allow agents to propose updates to task statuses (e.g., mark as "completed", "verified", "in review") and to integrate with an external task management system.
* **Location**: `templates/mcp_definitions/task_tracker_mcp.json`
* **`task_tracker_mcp.json` Definition**:
    ```json
    {
      "tool_name": "TaskTrackerMCP",
      "description": "Allows agents to propose updates to the status of tasks defined in the Research & Planning Document or external task trackers. Requires human approval for all status changes.",
      "api_endpoint": "http://10.0.0.2:80XX/task", // Replace 80XX with a unique port
      "request_schema": {
        "type": "object",
        "properties": {
          "task_id": {
            "type": "string",
            "description": "A unique identifier for the task to be updated (e.g., a section heading from the plan, or an external ticket ID)."
          },
          "status": {
            "type": "string",
            "enum": ["in_progress", "completed", "verified", "failed", "blocked", "awaiting_review"],
            "description": "The new status to set for the task."
          },
          "notes": {
            "type": "string",
            "description": "Optional: Any relevant notes or context for the status update."
          },
          "output_file_path": {
            "type": "string",
            "description": "Optional: Path to the file containing the agent's output related to this task (e.g., generated code, test report)."
          }
        },
        "required": ["task_id", "status"]
      },
      "response_format": {
        "type": "object",
        "properties": {
          "status": {"type": "string"},
          "message": {"type": "string"},
          "updated_task_id": {"type": "string"}
        }
      },
      "access_control": {
        "Code Review Agent": "permissioned_access",
        "Overseer Agent": "permissioned_access",
        "Unit Tester Agent": "permissioned_access",
        "Coder Agent": "permissioned_access",
        "Planning Agent": "permissioned_access",
        "Documentation Agent": "permissioned_access",
        "Refactor Agent": "permissioned_access",
        "n8n Flow Creator Agent": "permissioned_access"
      },
      "agent_specific_guidance": {
        "Code Review Agent": "After successfully reviewing code and confirming its quality/security, or after verifying tests, use TaskTrackerMCP to mark the corresponding task as 'verified' or 'awaiting_review'. Provide the 'task_id' and relevant 'notes'. This action requires human approval.",
        "Overseer Agent": "To update the status of high-level project phases or aggregated sub-tasks, use TaskTrackerMCP. You may mark tasks as 'completed' or 'failed' based on your monitoring, but remember this requires human approval.",
        "Unit Tester Agent": "Upon successful execution of unit tests and validation of code, use TaskTrackerMCP to mark the corresponding code implementation task as 'tested' or 'awaiting_review' for further human inspection. This requires human approval.",
        "Coder Agent": "Once you have completed a coding task as per the plan and generated your output, use TaskTrackerMCP to mark the task as 'awaiting_review'. Include the 'output_file_path' to your generated code. This action requires human approval.",
        "Planning Agent": "After a comprehensive plan has been drafted and is ready for human review, you may propose marking the planning phase as 'awaiting_review' using TaskTrackerMCP. This requires human approval.",
        "Documentation Agent": "When a documentation task is complete, use TaskTrackerMCP to mark it as 'completed' and provide the 'output_file_path' to the generated documentation. This requires human approval.",
        "Refactor Agent": "Upon completion of a refactoring task, use TaskTrackerMCP to mark the task as 'awaiting_review', indicating it's ready for human inspection and potential testing. This requires human approval.",
        "n8n Flow Creator Agent": "After generating a complete n8n workflow JSON, use TaskTrackerMCP to mark the workflow creation task as 'awaiting_review', providing the 'output_file_path' to the JSON. This requires human approval."
      }
    }
    ```
* **Backend Implementation**: The `TaskTrackerMCP` service itself would be a small Python FastAPI application (similar to SecretsMCP) running on the AI Workhorse. It would expose an endpoint (e.g., `/task`) that accepts the `task_id`, `status`, and `notes`. Its internal logic would then update a persistent store (e.g., a simple JSON file on disk, a SQLite database, or an actual API call to Todoist/Jira if configured).

### 2. Enhanced Agent Prompting and Feedback Loop

* **Agent System Prompts**: All agent system prompts will already contain the `--- COMMON_AGENT_COMPONENTS_PLACEHOLDER ---`, which includes the `Tool Interaction Protocol` and the dynamic injection points for `Available Tools` and `Tool-Specific Guidance`. The `TaskTrackerMCP`'s guidance will be dynamically injected for relevant agents.
* **"Human Feedback" Context**: The existing mechanism in `ai_rails_backend.py` to feed back `Human Feedback:` and `PREVIOUS TOOL OUTPUT` is crucial. This will be used extensively when:
    * A `tool_request` (including `TaskTrackerMCP`) fails validation.
    * A `tool_request` is denied by the human.
    * An agent's overall output (code, plan, document) is deemed unsatisfactory by the human.

### 3. Output Validation & Linter Integration

To prevent "lazy LLM" output and enforce correctness beyond just tool requests:

* **`jsonschema` Validation for Tool Requests**: Implement the `jsonschema` validation within `ai_rails_backend.py`'s `engage_agent` function, specifically for validating the `parameters` of any `tool_request` against the MCP's `request_schema`.
    * If validation fails, the agent receives specific, actionable feedback on *why* the JSON was malformed or incorrect, forcing a retry.
* **Post-Processing Output Validation (`ai_rails_backend.py`)**:
    * After an agent generates its primary output (e.g., Markdown plan, code block, n8n JSON), `ai_rails_backend.py` would trigger agent-specific validation logic.
    * **For Coder Agent outputs**: Integrate linters (e.g., `flake8` for Python, `ESLint` for JS) or formatters (`Black`, `Prettier`) as optional post-processing steps. If code fails linting, the `ai_rails_backend.py` sends feedback to the Coder Agent (`Human/System Feedback: Your code failed linting with errors X, Y, Z. Please revise.`).
    * **For n8n Flow Creator Agent outputs**: Validate the generated JSON against a known n8n workflow schema or a simpler set of validation rules (e.g., ensure required top-level keys are present, nodes have basic structure).
    * **For Documentation Agent outputs**: Simple checks for Markdown formatting, presence of required headings, etc.
    * **Automated Retry**: If validation fails, `ai_rails_backend.py` automatically re-engages the agent with the validation feedback, prompting it to self-correct and retry.

### 4. GUI Integration (Future UI / Dashboard)

This feature heavily relies on the "Simple UI / Dashboard" to be truly effective.

* **Task List Display**: The UI would parse the "Research & Planning Document" to extract tasks (e.g., headings or specific checklist items) and display them in a visual list or Kanban board.
* **Status Indicators**: Each task would have a status indicator. When `TaskTrackerMCP` is successfully executed (and human-approved), the UI updates the status visually by reading the `ai-rails.log`.
* **Interactive Checkboxes/Buttons**: The UI could present interactive elements that, when clicked, would propose `TaskTrackerMCP` calls to the human, making the "marking off" process seamless.
* **Diff Viewer for Code Review**: The UI's diff viewer would be critical for human approval of code before a task is marked as "verified."

### Required Pre-requisite / Easier to Implement First Features:

This feature largely builds on existing or planned capabilities, but some would significantly ease its implementation:

1.  **Simple UI / Dashboard (MVP Priority)**: This is **highly recommended** to be prioritized before this "Task Tracking and Learning System." While the backend logic for task tracking can be built, without the UI, marking tasks off lists would be a purely terminal-based, less intuitive experience. The visual feedback and interactive approval in the GUI are central to the user experience of task tracking.
2.  **Overseer Daemon**: This is **required** if the Overseer Agent is to play a role in task tracking or anomaly-based learning (e.g., detecting if a deployed feature is actually working as expected by monitoring logs). The daemon's ability to monitor `ai-rails.log` is essential for triggering proactive task status changes (e.g., marking a task "failed" if critical errors appear after deployment).
3.  **MCP-Sequential-Thinking**: While not strictly a prerequisite, having this MCP would make it easier for the Planning Agent (or other agents) to generate highly structured task breakdowns in the "Research & Planning Document" with clear `task_id` potential, which simplifies the `TaskTrackerMCP`'s job.
4.  **Code Executor MCP**: This is important for the Unit Tester Agent to *verify* code, which then allows it to confidently propose marking a task as "tested" or "verified" via `TaskTrackerMCP`.
5.  **Robust `ai_rails_backend.py` & `call_mcp.py` Infrastructure (Already Done/In Progress)**: The current efforts to dynamically load MCP definitions and create flexible `call_mcp.py` routing are fundamental. The `jsonschema` validation is also a direct prerequisite for robust input enforcement.

By implementing these, you'll create a powerful system that not only gets tasks done but also provides a clear, verifiable record of progress and continuously improves its own performance through structured feedback.