# Changelog

All notable changes to AI Rails will be documented in this file.

## [Unreleased]

### Added
- Project-scoped secrets support in SecretsMCP
  - Agents can now use project-specific API keys and secrets
  - Automatic fallback from PROJECT__SECRET_NAME to global SECRET_NAME
  - Project context set via AI_RAILS_PROJECT_NAME environment variable
- New documentation:
  - PROJECT_SECRETS_GUIDE.md - Comprehensive guide for managing multi-project secrets
  - CUSTOM_MCP_SETUP.md - Instructions for deploying MCP services
  - MCP_DEVELOPMENT_GUIDE.md - Guide for creating custom MCPs
  - COMMUNITY_MCPS.md - Framework for community contributions
- Helper scripts:
  - scripts/set-project-context.sh - Manage project context for secrets
  - scripts/setup-personal-config.sh - Create personal configuration layer
  - scripts/prepare-public-release.sh - Prepare repository for public release
- Docker support:
  - docker/mcp-services.yml - Mock MCP services for testing
- Infrastructure-agnostic configuration:
  - All hardcoded IPs replaced with localhost in .example.env
  - Personal configuration layer keeps infrastructure details separate
- Simple UI/Dashboard section added to main documentation (MVP feature)

### Changed
- Updated .gitignore to protect personal configuration files
- Modified call_mcp.py to support project-scoped secret requests
- Enhanced ai_rails_backend.py to show project context in prompts
- Updated test_secrets_flow.py with project-scoped secret tests
- Improved README.md with prerequisites and MCP service information

### Security
- Sensitive secrets list in ai_rails_backend.py for enhanced approval flow
- Project isolation for client API keys and secrets
- Authentication required for SecretsMCP access

## [1.0.0] - Initial Release

### Added
- Core AI Rails workflow system
- Bounded AI agent architecture
- Human-in-the-loop approval system
- File-based communication protocol
- Support for local (Ollama) and remote (Claude) LLMs
- MCP (Model Context Provider) integration framework
- Comprehensive logging and auditability
- Template system for agent prompts
- SecretsMCP for secure API key management