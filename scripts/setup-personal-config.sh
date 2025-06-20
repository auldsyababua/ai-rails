#!/bin/bash

# setup-personal-config.sh
# This script helps set up a personal configuration layer for AI Rails
# that keeps your infrastructure details separate from the public repository

set -e

echo "=== AI Rails Personal Configuration Setup ==="
echo

# Check if personal config repo path is set
PERSONAL_CONFIG_DIR="${AI_RAILS_CONFIG_DIR:-$HOME/ai-rails-config}"

# Function to create personal config structure
create_personal_config() {
    echo "Creating personal configuration at: $PERSONAL_CONFIG_DIR"
    
    mkdir -p "$PERSONAL_CONFIG_DIR"/{envs,scripts,docs,mcp-deployments}
    
    # Create a sample personal env file
    cat > "$PERSONAL_CONFIG_DIR/envs/personal.env.example" << 'EOF'
# Personal AI Rails Configuration
# Copy this to personal.env and fill in your values

# Your specific infrastructure IPs
OLLAMA_BASE_URL=http://10.0.0.2:11434
SECRETS_MCP_URL=http://10.0.0.2:8004
CODEBASE_SUMMARY_MCP_URL=http://10.0.0.2:8003
MCP_SEQUENTIAL_THINKING_URL=http://10.0.0.2:8001
CONTEXT7_URL=http://10.0.0.2:8002
BRAVE_SEARCH_MCP_URL=http://10.0.0.2:8005
N8N_WEBHOOK_BASE_URL=http://192.168.1.3:80/n8n/webhook/

# Your API keys (these should come from SecretsMCP in production)
AI_RAILS_SECRETS_MCP_AUTH_TOKEN=your-secure-auth-token-here

# Project context (optional - for project-specific secrets)
# AI_RAILS_PROJECT_NAME=ai-rails
EOF

    # Create activation script
    cat > "$PERSONAL_CONFIG_DIR/scripts/activate.sh" << 'EOF'
#!/bin/bash
# Activate personal AI Rails configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")"

# Source the personal environment
if [ -f "$CONFIG_DIR/envs/personal.env" ]; then
    echo "Loading personal AI Rails configuration..."
    set -a
    source "$CONFIG_DIR/envs/personal.env"
    set +a
    echo "Personal configuration loaded from: $CONFIG_DIR/envs/personal.env"
else
    echo "Warning: Personal env file not found at $CONFIG_DIR/envs/personal.env"
    echo "Copy personal.env.example to personal.env and configure it."
fi
EOF
    chmod +x "$PERSONAL_CONFIG_DIR/scripts/activate.sh"

    # Create a README for personal config
    cat > "$PERSONAL_CONFIG_DIR/README.md" << 'EOF'
# AI Rails Personal Configuration

This directory contains your personal AI Rails configuration that should NOT be committed to the main repository.

## Structure

- `envs/` - Environment files with your specific IPs and configurations
- `scripts/` - Helper scripts for managing your configuration
- `docs/` - Your personal deployment documentation
- `mcp-deployments/` - Your custom MCP deployment configurations

## Usage

1. Copy `envs/personal.env.example` to `envs/personal.env`
2. Edit with your specific values
3. Source the configuration: `source scripts/activate.sh`
4. Run AI Rails normally

## Security

Keep this directory private and never commit it to public repositories.
EOF

    echo "Personal configuration structure created!"
}

# Function to link personal config to current project
link_personal_config() {
    echo
    echo "Linking personal configuration to current AI Rails project..."
    
    # Create symlink to personal env if it exists
    if [ -f "$PERSONAL_CONFIG_DIR/envs/personal.env" ]; then
        ln -sf "$PERSONAL_CONFIG_DIR/envs/personal.env" .env.personal
        echo "Linked personal.env to .env.personal"
    fi
    
    # Create local activation script
    cat > .activate-personal.sh << EOF
#!/bin/bash
# Quick activation script for this project
source "$PERSONAL_CONFIG_DIR/scripts/activate.sh"
EOF
    chmod +x .activate-personal.sh
    
    echo "Personal configuration linked!"
}

# Main execution
if [ -d "$PERSONAL_CONFIG_DIR" ]; then
    echo "Personal configuration directory already exists at: $PERSONAL_CONFIG_DIR"
    read -p "Link to current project? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        link_personal_config
    fi
else
    echo "Personal configuration directory not found."
    read -p "Create new personal configuration? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_personal_config
        link_personal_config
    fi
fi

echo
echo "=== Setup Complete ==="
echo
echo "Next steps:"
echo "1. Edit your personal configuration: $PERSONAL_CONFIG_DIR/envs/personal.env"
echo "2. Activate it: source .activate-personal.sh"
echo "3. Run AI Rails: ./run_workflow.sh"
echo
echo "Remember: Your personal configuration is gitignored and won't be committed."