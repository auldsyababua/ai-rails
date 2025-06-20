# Project-Scoped Secrets Guide

This guide explains how to manage secrets for multiple projects using AI Rails' project-scoped secrets feature.

## Overview

AI Rails supports project-specific API keys and secrets, allowing you to:
- Use different API keys for different projects (e.g., separate billing)
- Keep client secrets isolated from personal projects
- Fall back to global defaults when no project-specific secret exists
- Maintain one master secrets file on your secure Workhorse server

## How It Works

### 1. Naming Convention

Secrets are stored using a `PROJECT__SECRET_NAME` format:

```env
# Global default
OPENAI_API_KEY=sk-proj-global-default

# Project-specific
AI_RAILS__OPENAI_API_KEY=sk-proj-ai-rails-specific
CLIENT_WORK__OPENAI_API_KEY=sk-proj-client-billing
PERSONAL_BLOG__OPENAI_API_KEY=sk-proj-blog-quota
```

### 2. Lookup Order

When SecretsMCP receives a request for `OPENAI_API_KEY` with project context `client-work`:
1. First checks: `CLIENT_WORK__OPENAI_API_KEY`
2. Falls back to: `OPENAI_API_KEY` (global)
3. Returns error if neither exists

### 3. Setting Project Context

Three ways to set project context:

**Option A - Environment Variable (Recommended):**
```bash
export AI_RAILS_PROJECT_NAME=client-work
./run_workflow.sh
```

**Option B - Using Helper Script:**
```bash
./scripts/set-project-context.sh client-work
# or interactive mode:
./scripts/set-project-context.sh
```

**Option C - In Personal Config:**
Add to `~/ai-rails-config/scripts/activate.sh`:
```bash
export AI_RAILS_PROJECT_NAME=ai-rails
```

## Setting Up Your Master Secrets File

On your Workhorse at `/opt/secrets-mcp/.env`:

```env
# ========== GLOBAL DEFAULTS ==========
# Used when no project-specific key exists
ANTHROPIC_API_KEY=sk-ant-api03-global
OPENAI_API_KEY=sk-proj-global
GITHUB_TOKEN=ghp_global_token
DB_PASSWORD=global_db_pass

# ========== PROJECT: ai-rails ==========
# Keys for AI Rails development
AI_RAILS__ANTHROPIC_API_KEY=sk-ant-api03-ai-rails
AI_RAILS__OPENAI_API_KEY=sk-proj-ai-rails
AI_RAILS__GITHUB_TOKEN=ghp_ai_rails_token

# ========== PROJECT: client-abc ==========
# Keys for Client ABC work
CLIENT_ABC__OPENAI_API_KEY=sk-proj-client-abc
CLIENT_ABC__STRIPE_API_KEY=sk-live-client-abc
CLIENT_ABC__SENDGRID_API_KEY=client-abc-sendgrid
CLIENT_ABC__DB_PASSWORD=client_abc_prod_pass

# ========== PROJECT: personal-blog ==========
# Keys for personal website
PERSONAL_BLOG__OPENAI_API_KEY=sk-proj-personal
PERSONAL_BLOG__CLOUDFLARE_API_KEY=blog-cf-key
PERSONAL_BLOG__ANALYTICS_KEY=blog-analytics

# ========== SHARED INFRASTRUCTURE ==========
# These don't change per project
SECRETS_MCP_AUTH_KEY=your-secure-auth-token
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=http://localhost:9200
```

## Common Use Cases

### 1. Client Work Isolation
Keep client API keys separate from personal projects:
```bash
# When working on client project
export AI_RAILS_PROJECT_NAME=client-abc
./run_workflow.sh
# Uses CLIENT_ABC__OPENAI_API_KEY for all OpenAI calls
```

### 2. Development vs Production
Use different keys for development and production:
```bash
# Development
export AI_RAILS_PROJECT_NAME=myapp-dev
# Uses MYAPP_DEV__DATABASE_URL

# Production
export AI_RAILS_PROJECT_NAME=myapp-prod
# Uses MYAPP_PROD__DATABASE_URL
```

### 3. Cost Tracking
Use different API keys to track costs per project:
```env
# Each project gets its own OpenAI key for billing
PROJECT_A__OPENAI_API_KEY=sk-proj-a-billing
PROJECT_B__OPENAI_API_KEY=sk-proj-b-billing
PROJECT_C__OPENAI_API_KEY=sk-proj-c-billing
```

## Best Practices

### 1. Naming Projects
Use consistent, descriptive project names:
- ✅ `client-acme`, `personal-blog`, `startup-mvp`
- ❌ `proj1`, `test`, `new`

### 2. Documentation
Keep a list of your projects in your personal config:
```markdown
# ~/ai-rails-config/docs/my-projects.md
- ai-rails: AI Rails development
- client-acme: ACME Corp website
- personal-blog: My tech blog
- startup-idea: Secret startup project
```

### 3. Security
- Never commit the master `.env` file
- Use strong, unique API keys per project
- Regularly rotate keys for sensitive projects
- Monitor usage per project

### 4. Global Fallbacks
Always set sensible global defaults:
- Development/testing keys as globals
- Production keys as project-specific
- Shared infrastructure (Redis, etc.) as globals

## Troubleshooting

### Secret Not Found
```
Error: Secret 'OPENAI_API_KEY' not found
```
Check:
1. Is `AI_RAILS_PROJECT_NAME` set correctly?
2. Does `PROJECT__OPENAI_API_KEY` exist in master .env?
3. Does global `OPENAI_API_KEY` exist as fallback?

### Wrong Project Context
```bash
# Check current context
echo $AI_RAILS_PROJECT_NAME

# Or use helper
./scripts/set-project-context.sh --show
```

### Testing Secrets
```bash
# Test specific project's secrets
AI_RAILS_PROJECT_NAME=client-work python test_secrets_flow.py
```

## Migration Guide

### From Flat Structure
If you currently have:
```env
OPENAI_API_KEY=sk-proj-mixed-use
STRIPE_API_KEY=sk-live-mixed-use
```

Migrate to:
```env
# Global defaults (for personal use)
OPENAI_API_KEY=sk-proj-personal
STRIPE_API_KEY=sk-test-personal

# Client-specific
CLIENT_WORK__OPENAI_API_KEY=sk-proj-client
CLIENT_WORK__STRIPE_API_KEY=sk-live-client
```

### Gradual Migration
You don't need to migrate everything at once:
1. Keep existing keys as globals
2. Add project-specific keys as needed
3. SecretsMCP handles the fallback logic

## Advanced Features

### 1. Environment-Specific Projects
```env
# Development environment for project
MYAPP_DEV__DATABASE_URL=postgres://localhost/myapp_dev
MYAPP_DEV__REDIS_URL=redis://localhost:6379/0

# Staging environment
MYAPP_STAGING__DATABASE_URL=postgres://staging.server/myapp
MYAPP_STAGING__REDIS_URL=redis://staging.server:6379/0

# Production environment
MYAPP_PROD__DATABASE_URL=postgres://prod.server/myapp
MYAPP_PROD__REDIS_URL=redis://prod.server:6379/0
```

### 2. Dynamic Project Selection
In your scripts:
```bash
#!/bin/bash
# deploy.sh
ENVIRONMENT=$1  # dev, staging, prod
export AI_RAILS_PROJECT_NAME="myapp-${ENVIRONMENT}"
./run_workflow.sh
```

### 3. Project Aliases
Create shortcuts in your shell profile:
```bash
# ~/.zshrc or ~/.bashrc
alias work-on-client='export AI_RAILS_PROJECT_NAME=client-abc'
alias work-on-blog='export AI_RAILS_PROJECT_NAME=personal-blog'
alias work-on-ai-rails='export AI_RAILS_PROJECT_NAME=ai-rails'
```

## Next Steps

1. Set up your master secrets file on Workhorse
2. Organize secrets by project using the naming convention
3. Set project context before running AI Rails
4. Enjoy isolated, secure secret management!