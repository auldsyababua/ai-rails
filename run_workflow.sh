#!/bin/bash

# AI Rails Workflow Orchestrator (Bootstrapper for Python Backend)
# This script launches the ai_rails_backend.py Python script,
# which handles the core AI-assisted engineering workflow.

PROJECT_ROOT=$(pwd)
TEMPLATES_DIR="$PROJECT_ROOT/templates"
OUTPUT_DIR="$PROJECT_ROOT/output"
PYTHON_BACKEND="$PROJECT_ROOT/ai_rails_backend.py"

echo "-----------------------------------------"
echo "           Welcome to AI Rails!          "
echo "-----------------------------------------"
echo "Launching the AI Rails Python backend..."
echo ""

# Check for Python and required libraries
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 to run AI Rails."
    exit 1
fi

# It's good practice to run in a virtual environment
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt # Ensure dependencies are installed

# --- Main Menu ---
echo "What are you looking to do today?"
echo "1) Start a NEW Project (from scratch)"
echo "2) Add/Update a FEATURE to an existing project"
echo "3) Enter EXECUTION Phase (Code, Test, Document, n8n Flows)"
echo "Q) Quit AI Rails"
echo ""
read -p "Enter your choice (1, 2, 3, or Q): " choice

case "$choice" in
    1)
        # --- NEW PROJECT Workflow ---
        echo ""
        echo "--- Phase 1: New Project Kick-off ---"
        read -p "Please enter a short, hyphen-separated name for your new project (e.g., my-learning-app): " project_name
        if [ -z "$project_name" ]; then
            echo "Project name cannot be empty. Exiting."
            exit 1
        fi

        NEW_PROJECT_PATH="$OUTPUT_DIR/new_project_plans/$project_name"
        mkdir -p "$NEW_PROJECT_PATH"
        cp "$TEMPLATES_DIR/new_project_kickoff_template.md" "$NEW_PROJECT_PATH/initial_project_idea.md"

        echo ""
        echo "Successfully created project directory: $NEW_PROJECT_PATH"
        echo "Copied 'new_project_kickoff_template.md' to '$NEW_PROJECT_PATH/initial_project_idea.md'."
        echo ""
        echo "ACTION REQUIRED: Open '$NEW_PROJECT_PATH/initial_project_idea.md' in your text editor."
        echo "Fill out the template with a detailed explanation of your new project idea."
        echo "Save and close the file when done."
        echo ""
        read -p "Press Enter once you have filled out 'initial_project_idea.md' and are ready to proceed with AI planning."

        # Launch the Python backend for Planning Agent
        python3 "$PYTHON_BACKEND" "$project_name" "new_project"
        ;;
    2)
        # --- FEATURE/UPDATE Workflow ---
        echo ""
        echo "--- Phase 1: Feature/Update Kick-off ---"
        read -p "Please enter a short, hyphen-separated name for this feature/update (e.g., infinite-scroll-briefs): " feature_name
        if [ -z "$feature_name" ]; then
            echo "Feature name cannot be empty. Exiting."
            exit 1
        fi

        FEATURE_PATH="$OUTPUT_DIR/feature_update_plans/$feature_name"
        mkdir -p "$FEATURE_PATH"
        cp "$TEMPLATES_DIR/feature_update_kickoff_template.md" "$FEATURE_PATH/feature_update_idea.md"

        echo ""
        echo "Successfully created feature directory: $FEATURE_PATH"
        echo "Copied 'feature_update_kickoff_template.md' to '$FEATURE_PATH/feature_update_idea.md'."
        echo ""
        echo "ACTION REQUIRED: Open '$FEATURE_PATH/feature_update_idea.md' in your text editor."
        echo "Fill out the template with a detailed explanation of your feature/update, INCLUDING all relevant codebase context (file paths, existing functions, design patterns)."
        echo "Save and close the file when done."
        echo ""
        read -p "Press Enter once you have filled out 'feature_update_idea.md' and are ready to proceed with AI planning."

        # Launch the Python backend for Planning Agent
        python3 "$PYTHON_BACKEND" "$feature_name" "feature_update"
        ;;
    3)
        # --- EXECUTION Phase ---
        echo ""
        echo "--- Phase 3: Execution ---"
        read -p "Please enter the full path to the directory containing your FINALIZED plan (e.g., $OUTPUT_DIR/new_project_plans/my-learning-app): " plan_dir_raw
        
        # Resolve to absolute path, handling ~
        PLAN_DIR=$(eval echo "$plan_dir_raw")

        if [ ! -d "$PLAN_DIR" ]; then
            echo "Error: Directory not found. Please provide a valid path. Exiting."
            exit 1
        fi

        # Find the latest plan.md or similar
        FINAL_PLAN_FILE=""
        if [ -f "$PLAN_DIR/final_plan.md" ]; then
            FINAL_PLAN_FILE="$PLAN_DIR/final_plan.md"
        elif [ -f "$PLAN_DIR/initial_plan.md" ]; then
            FINAL_PLAN_FILE="$PLAN_DIR/initial_plan.md"
        elif [ -f "$PLAN_DIR/initial_feature_plan.md" ]; then # For feature updates
            FINAL_PLAN_FILE="$PLAN_DIR/initial_feature_plan.md"
        else
            # Try to find any markdown file in the directory
            latest_plan=$(ls -t "$PLAN_DIR"/*.md 2>/dev/null | head -n 1)
            if [ -n "$latest_plan" ]; then
                FINAL_PLAN_FILE="$latest_plan"
            fi
        fi

        if [ -z "$FINAL_PLAN_FILE" ]; then
            echo "Error: No plan file (e.g., final_plan.md, initial_plan.md, initial_feature_plan.md, or any other .md) found in '$PLAN_DIR'. Exiting."
            exit 1
        fi

        echo "Using plan file: $FINAL_PLAN_FILE"
        echo ""

        # Launch the Python backend for Execution Phase
        # Pass the plan file path as the third argument
        python3 "$PYTHON_BACKEND" "$(basename "$PLAN_DIR")" "execution" "$FINAL_PLAN_FILE"
        ;;
    q|Q)
        echo "Exiting AI Rails. Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please enter 1, 2, 3, or Q."
        ;;
esac

echo "-----------------------------------------"
echo "AI Rails: Workflow initiated via Python backend."
echo "Follow prompts from the Python script in your terminal."
echo "-----------------------------------------"