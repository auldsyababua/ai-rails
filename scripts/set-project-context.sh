#!/bin/bash

# set-project-context.sh
# This script helps set the project context for AI Rails to use project-specific secrets

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Rails Project Context Manager ===${NC}"
echo

# Function to display current context
show_current_context() {
    if [ -n "$AI_RAILS_PROJECT_NAME" ]; then
        echo -e "Current project context: ${GREEN}$AI_RAILS_PROJECT_NAME${NC}"
    else
        echo -e "No project context set (using global secrets)"
    fi
}

# Function to list example projects
list_example_projects() {
    echo -e "\n${YELLOW}Example project names:${NC}"
    echo "  - ai-rails        (AI Rails development)"
    echo "  - client-work     (Client projects)"
    echo "  - personal-blog   (Personal website)"
    echo "  - testing         (Test projects)"
    echo "  - production      (Production deployments)"
}

# Function to set project context
set_context() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        echo -e "${YELLOW}Clearing project context...${NC}"
        unset AI_RAILS_PROJECT_NAME
        echo -e "${GREEN}Project context cleared. Now using global secrets.${NC}"
    else
        export AI_RAILS_PROJECT_NAME="$project_name"
        echo -e "${GREEN}Project context set to: $project_name${NC}"
        echo
        echo "SecretsMCP will now look for secrets in this order:"
        echo "  1. ${project_name^^}__SECRET_NAME"
        echo "  2. SECRET_NAME (global fallback)"
    fi
}

# Main menu
if [ $# -eq 0 ]; then
    # Interactive mode
    show_current_context
    list_example_projects
    
    echo
    echo "Options:"
    echo "  1) Set new project context"
    echo "  2) Clear project context (use global)"
    echo "  3) Exit"
    echo
    read -p "Choose an option (1-3): " choice
    
    case $choice in
        1)
            read -p "Enter project name: " project_name
            set_context "$project_name"
            ;;
        2)
            set_context ""
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Invalid option${NC}"
            exit 1
            ;;
    esac
else
    # Command line mode
    case "$1" in
        --clear|-c)
            set_context ""
            ;;
        --show|-s)
            show_current_context
            ;;
        --list|-l)
            list_example_projects
            ;;
        --help|-h)
            echo "Usage: $0 [project-name|option]"
            echo
            echo "Options:"
            echo "  project-name    Set the project context"
            echo "  --clear, -c     Clear project context"
            echo "  --show, -s      Show current context"
            echo "  --list, -l      List example projects"
            echo "  --help, -h      Show this help"
            echo
            echo "Examples:"
            echo "  $0 ai-rails     # Set context to ai-rails project"
            echo "  $0 --clear      # Clear context (use global secrets)"
            echo "  $0              # Interactive mode"
            ;;
        *)
            set_context "$1"
            ;;
    esac
fi

echo
echo -e "${BLUE}To make this permanent for your session:${NC}"
echo "  export AI_RAILS_PROJECT_NAME=\"$AI_RAILS_PROJECT_NAME\""
echo
echo -e "${BLUE}Or add to your personal config activate script:${NC}"
echo "  echo 'export AI_RAILS_PROJECT_NAME=\"$AI_RAILS_PROJECT_NAME\"' >> ~/ai-rails-config/scripts/activate.sh"