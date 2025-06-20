# AI Rails

A human-centric, bounded AI engineering workflow system that prioritizes safety, transparency, and developer control while leveraging the power of AI agents for software development.

## Philosophy & Safety First

This workflow explicitly adopts a "dumb orchestrator" approach to AI safety, informed by principles like instrumental convergence and mesa-optimization concerns.

* **Dumb Orchestrator:** The `run_workflow.sh` script is a simple, rule-based state machine. It does **not** contain any AI decision-making logic. Its sole purpose is to guide *you* through the process, telling you which templates to use, how to interact with AI agents (like Claude Code), and when to review outputs. This prevents any single AI from inheriting "god mode" capabilities.
* **Agent Compartmentalization & Rails:** AI intelligence is confined to individual agents (e.g., Claude Code), which operate within strict boundaries defined by their system prompts and the structured inputs they receive. They are on "rails" both by their internal instructions (prompts) and by the explicit steps in this workflow.
* **Human-in-the-Loop Boundaries:** Critical decision points, especially planning review and code execution, always require explicit human approval. This ensures human oversight and "taste" remain central to the engineering process.
* **Compounding Engineering:** The goal is to build reusable templates and a repeatable process that makes future engineering tasks progressively easier and more efficient. Each completed task refines the system.

## Workflow Overview

This workflow focuses on two primary use cases:

1.  **Starting a New Project:** From a high-level idea to a detailed technical plan.
2.  **Adding/Updating Features:** Integrating new functionality or fixes into an existing codebase.

The process is guided by the `run_workflow.sh` script, which will lead you through distinct phases:

* **Phase 1: Initial Prompting & Entering "Plan Mode"**
    * Choose your workflow (New Project / Edit Existing).
    * Prepare your initial prompt using a specific template.
    * Engage Claude Code with its "Planning Agent" system prompt and your initial idea.
* **Phase 2: Iterative Planning & Refinement (Human-AI Collaboration)**
    * Review Claude Code's initial plan.
    * Provide feedback and ask Claude Code to refine specific sections.
    * Repeat until the plan is comprehensive and actionable.
* **Phase 3: Execution (and beyond - Future Expansion)**
    * Once the plan is finalized, use it to guide code generation, testing, and deployment. (Future enhancements will integrate more AI agents here, also on rails).

## Prerequisites

### Core Requirements
- Python 3.9+
- Claude API access (or local Ollama setup with Qwen2.5-coder:32b)
- Docker (recommended) or custom MCP deployment

### MCP Services
AI Rails uses Model Context Providers (MCPs) for enhanced functionality:

- **SecretsMCP**: Secure API key management (see [Custom MCP Setup](docs/CUSTOM_MCP_SETUP.md))
- **CodebaseSummaryMCP**: Project context for agents
- **Other MCPs**: Sequential thinking, web search, etc.

For production use, deploy our reference MCP implementations or create your own following our [MCP Development Guide](docs/MCP_DEVELOPMENT_GUIDE.md).

## Quick Start

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/colinaulds/ai-rails.git
    cd ai-rails
    ```
    
2.  **Set up environment:**
    ```bash
    cp .example.env .env
    # Edit .env with your configuration
    ```
    
3.  **Deploy MCP services (choose one):**
    
    **Option A - Use Docker mocks (for testing):**
    ```bash
    docker-compose -f docker/mcp-services.yml up
    ```
    
    **Option B - Deploy real MCPs:**
    See [Custom MCP Setup](docs/CUSTOM_MCP_SETUP.md)
    
4.  **Run the workflow:**
    ```bash
    ./run_workflow.sh
    ```
    The script will guide you through each step.

## Templates

* `templates/planning_agent_system_prompt.md`: Defines Claude Code's role as your planning expert. **Always provide this to Claude Code at the start of a planning session.**
* `templates/new_project_kickoff_template.md`: Use this when starting a new project.
* `templates/feature_update_kickoff_template.md`: Use this when working on an existing project.
* *(Future: Add templates for code generation, testing, documentation, etc., each with their own specific agent rails/prompts.)*

## Output & Archiving

* `output/`: This is where your generated "Research & Planning Documents" will be saved.
* `archived_plans/`: Move completed or deprecated plans here to keep `output/` clean.

## Adding Project-Specific MCPs

AI Rails supports project-specific MCP integrations. To add MCPs for your project:

1. Create `.ai-rails/mcp_definitions/` in your project root
2. Add MCP definition JSON files (e.g., `todoist_mcp.json`)
3. Configure MCP URLs in your `.env` file
4. The agents will automatically discover and use these MCPs

See [MCP Development Guide](docs/MCP_DEVELOPMENT_GUIDE.md) for details.

## Community

- **MCP Implementations**: Check our [Community MCPs](docs/COMMUNITY_MCPS.md) page
- **Contributing**: We welcome contributions! Please read our contributing guidelines
- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join our discussions for questions and ideas

## Documentation

- [Deep Explanation](docs/DEEP-EXPLANATION.md) - Detailed architecture and philosophy
- [Custom MCP Setup](docs/CUSTOM_MCP_SETUP.md) - Deploy MCP services
- [MCP Development Guide](docs/MCP_DEVELOPMENT_GUIDE.md) - Create your own MCPs
- [Community MCPs](docs/COMMUNITY_MCPS.md) - Community-contributed implementations
- [Project Secrets Guide](docs/PROJECT_SECRETS_GUIDE.md) - Managing secrets for multiple projects

## License

This project is licensed under the MIT License - see the LICENSE file for details.
