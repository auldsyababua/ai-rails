---
# CLAUDE.md for AI Rails Project

# This configuration file restricts Claude Code's capabilities when
# operating within the 'ai-engineering-workflow' repository.
# It enforces read-only access for core operations to prioritize safety
# and human oversight in this controlled environment.
---

# Global Restrictions:
# =====================
# This section overrides default Claude Code behaviors.

# Explicitly disable common destructive actions by making them read-only
# or by preventing their execution from this context.
# Note: Claude Code's exact capabilities and how to restrict them may evolve.
# Consult the latest Claude Code documentation for the most precise
# configuration options for blocking specific actions.

# Example of how you might restrict write/delete access to files:
# (These are conceptual. Real Claude Code restrictions may vary in syntax)
permissions:
  file_system:
    read: true  # Allow reading files
    write: false # Explicitly disable writing files
    create: false # Explicitly disable creating new files
    delete: false # Explicitly disable deleting files
  git:
    read: true   # Allow git status, diff, log
    write: false # Disable git commit, push, branch creation
  shell_commands:
    # Restrict shell commands to a safe subset for reading/information gathering
    # This is a very sensitive area; ensure any allowed commands are strictly necessary and safe.
    allowed_commands:
      - "ls"
      - "cat"
      - "grep"
      - "find"
      - "pwd"
      - "git status"
      - "git diff"
      - "git log"
      # IMPORTANT: If any agent needs to run more commands (e.g., install dependencies),
      # this should be facilitated via a human-approved MCP or manual step.
    default_action: "deny" # Deny all other commands by default

# System-wide context and instructions for Claude Code when in this repo.
# This supplements the agent-specific system prompts.
system_context:
  - "You are operating within a highly controlled and human-supervised environment named 'AI Rails'."
  - "For all operations within this repository, your file system access is strictly READ-ONLY. You cannot create, modify, or delete any files or directories."
  - "Your Git operations are also strictly READ-ONLY. You cannot make commits, push changes, or create branches."
  - "You are a specialized AI agent (e.g., Planner, Coder, Reviewer). Your output is for human review and approval. You do not autonomously execute changes to the project codebase."
  - "If asked to perform an action that involves writing, creating, or deleting, you must state that you are operating in a read-only context and cannot perform that action directly. Instead, you should formulate the *proposed change* in markdown (e.g., a code block of the desired new file, or a diff of changes) for human review and manual application."
  - "All tool requests (MCP queries, n8n automations) must be explicitly formulated in your output for human approval and execution. You do not execute tools directly."

# Additional models or configurations can be added here if needed for this repo.
# For instance, if you want specific models to be preferred for certain tasks within this repo.
# models:
#   default_coder: "qwen2.5-coder:32b"
#   default_reviewer: "claude-opus4"