#!/bin/bash

# AI Rails Workflow Orchestrator
# This script guides the user through the AI-assisted engineering planning process.
# It acts as a "dumb orchestrator," providing clear steps and ensuring human-in-the-loop decisions.

PROJECT_ROOT=$(pwd)
TEMPLATES_DIR="$PROJECT_ROOT/templates"
OUTPUT_DIR="$PROJECT_ROOT/output"

echo "-----------------------------------------"
echo "           Welcome to AI Rails!          "
echo "-----------------------------------------"
echo "This script will guide you through the AI-assisted planning workflow."
echo "Remember: I am a dumb orchestrator. I will tell you what to do, but"
echo "you are in control and responsible for interacting with Claude Code."
echo ""

# --- Main Menu ---
echo "What are you looking to do today?"
echo "1) Start a NEW Project (from scratch)"
echo "2) Add/Update a FEATURE to an existing project"
echo "3) Continue with EXECUTION Phase (Code, Test, Document)" # <--- ADD THIS LINE
echo "Q) Quit AI Rails"
echo ""
read -p "Enter your choice (1, 2, 3, or Q): " choice

case "$choice" in
    1)
        # --- NEW PROJECT Workflow ---
        echo ""
        echo "--- Phase 1: New Project Kick-off ---"
        echo "You've chosen to start a new project."
        echo ""
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
        read -p "Press Enter once you have filled out 'initial_project_idea.md' and are ready to proceed."

        echo ""
        echo "--- Engaging Claude Code (Planning Agent) ---"
        echo "Now, you will interact with Claude Code. Follow these steps precisely:"
        echo "1. Open Claude Code in your terminal (type 'claude' or your custom command)."
        echo "2. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/planning_agent_system_prompt.md' into Claude Code. This sets its 'rails'."
        echo "3. PASTE THE ENTIRE CONTENTS of '$NEW_PROJECT_PATH/initial_project_idea.md' into Claude Code."
        echo "4. Press Enter in Claude Code to let it generate the initial plan."
        echo ""
        echo "EXPECTED OUTPUT: Claude Code will generate a 'Research & Planning Document' based on your input."
        echo "ACTION REQUIRED: Carefully copy ALL of Claude Code's output."
        echo "Save Claude Code's output to: '$NEW_PROJECT_PATH/initial_plan.md'"
        echo ""
        read -p "Press Enter once you have saved Claude Code's initial plan to 'initial_plan.md'."

        echo ""
        echo "--- Phase 2: Iterative Planning & Refinement ---"
        echo "Now you have Claude Code's initial plan. This is where the human-AI collaboration shines."
        echo "1. OPEN '$NEW_PROJECT_PATH/initial_plan.md' in your text editor."
        echo "2. REVIEW the plan for accuracy, completeness, and alignment with your vision."
        echo "3. Go back to Claude Code. Provide feedback, ask clarifying questions, or request refinements."
        echo "   Example: 'Refine the "Implementation Plan" section to include more detail on API design.' or"
        echo "   Example: 'I need two alternative solutions for the data storage, with pros and cons for each.'"
        echo "4. Continue this dialogue, saving updated plans (e.g., 'plan_v2.md', 'plan_v3.md') in '$NEW_PROJECT_PATH'."
        echo ""
        echo "You are now in the iterative planning loop. Use your judgment to determine when the plan is sufficiently detailed and ready for execution."
        echo "Type 'exit' in Claude Code when you are done with the planning session for this task."
        ;;
    2)
        # --- FEATURE/UPDATE Workflow ---
        echo ""
        echo "--- Phase 1: Feature/Update Kick-off ---"
        echo "You've chosen to add/update a feature in an existing project."
        echo ""
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
        read -p "Press Enter once you have filled out 'feature_update_idea.md' and are ready to proceed."

        echo ""
        echo "--- Engaging Claude Code (Planning Agent) ---"
        echo "Now, you will interact with Claude Code. Follow these steps precisely:"
        echo "1. Open Claude Code in your terminal. For best context awareness, consider launching Claude Code from your *existing project's root directory* if it can access local files there."
        echo "2. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/planning_agent_system_prompt.md' into Claude Code. This sets its 'rails'."
        echo "3. PASTE THE ENTIRE CONTENTS of '$FEATURE_PATH/feature_update_idea.md' into Claude Code."
        echo "4. Press Enter in Claude Code to let it generate the initial plan."
        echo ""
        echo "EXPECTED OUTPUT: Claude Code will generate a 'Research & Planning Document' for your feature/update."
        echo "ACTION REQUIRED: Carefully copy ALL of Claude Code's output."
        echo "Save Claude Code's output to: '$FEATURE_PATH/initial_feature_plan.md'"
        echo ""
        read -p "Press Enter once you have saved Claude Code's initial plan to 'initial_feature_plan.md'."

        echo ""
        echo "--- Phase 2: Iterative Planning & Refinement ---"
        echo "Now you have Claude Code's initial plan. This is where the human-AI collaboration shines."
        echo "1. OPEN '$FEATURE_PATH/initial_feature_plan.md' in your text editor."
        echo "2. REVIEW the plan for accuracy, completeness, and alignment with your vision and existing codebase."
        echo "3. Go back to Claude Code. Provide feedback, ask clarifying questions, or request refinements."
        echo "   Example: 'Based on our current `BriefsAPI.js`, how would you modify step 3 to integrate with our existing authentication?' or"
        echo "   Example: 'Can you propose two ways to handle the infinite scroll state, considering we use Redux?'"
        echo "4. Continue this dialogue, saving updated plans (e.g., 'plan_v2.md', 'plan_v3.md') in '$FEATURE_PATH'."
        echo ""
        echo "You are now in the iterative planning loop. Use your judgment to determine when the plan is sufficiently detailed and ready for execution."
        echo "Type 'exit' in Claude Code when you are done with the planning session for this task."
        ;;
    q|Q)
        echo "Exiting AI Rails. Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please enter 1, 2, or Q."
        ;;
esac






case "$choice" in
    # ... (existing case for 1 and 2) ...

    3)
        # --- EXECUTION Phase ---
        echo ""
        echo "--- Phase 3: Execution (Code, Test, Document) ---"
        echo "You've chosen to enter the Execution Phase."
        echo ""
        read -p "Please enter the full path to the directory containing your FINALIZED plan (e.g., ~/Desktop/projects/ai-engineering-workflow/output/new_project_plans/my-learning-app): " plan_dir
        if [ ! -d "$plan_dir" ]; then
            echo "Error: Directory not found. Please provide a valid path. Exiting."
            exit 1
        fi

        # Find the latest plan.md or similar, prioritizing 'final_plan.md'
        FINAL_PLAN_FILE=""
        if [ -f "$plan_dir/final_plan.md" ]; then
            FINAL_PLAN_FILE="$plan_dir/final_plan.md"
        elif [ -f "$plan_dir/initial_plan.md" ]; then # Fallback if no final_plan yet
            FINAL_PLAN_FILE="$plan_dir/initial_plan.md"
        else
            # Try to find any markdown file in the directory
            latest_plan=$(ls -t "$plan_dir"/*.md 2>/dev/null | head -n 1)
            if [ -n "$latest_plan" ]; then
                FINAL_PLAN_FILE="$latest_plan"
            fi
        fi

        if [ -z "$FINAL_PLAN_FILE" ]; then
            echo "Error: No plan file (e.g., final_plan.md, initial_plan.md, or any other .md) found in '$plan_dir'. Exiting."
            exit 1
        fi

        echo "Using plan file: $FINAL_PLAN_FILE"
        echo ""

        # Sub-menu for Execution Phase
        while true; do
            echo "--- Execution Actions for '$plan_dir' ---"
            echo "A) Engage Coder Agent (Generate Code)"
            echo "B) Engage Unit Tester Agent (Generate Unit Tests)"
            echo "C) Engage Debugger Agent (Troubleshoot Code/Logs)"
            echo "D) Engage Documentation Agent (Generate Docs)"
            echo "E) Engage Code Review Agent (Review Code)"
            echo "F) Engage Refactor Agent (Refactor/Optimize Code)"
            echo "M) Back to Main Menu"
            echo "Q) Quit AI Rails"
            echo ""
            read -p "Choose an action: " exec_choice

            case "$exec_choice" in
                a|A)
                    # --- Coder Agent ---
                    echo ""
                    echo "--- Engaging Coder Agent ---"
                    echo "ACTION REQUIRED: Open Claude Code in your terminal."
                    echo "1. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/coder_agent_system_prompt.md' into Claude Code."
                    echo "2. PASTE THE ENTIRE CONTENTS of '$FINAL_PLAN_FILE' into Claude Code."
                    echo "3. Add any specific instructions for the coder (e.g., 'Focus on the database integration component and generate Python code for it.')."
                    echo "4. Press Enter in Claude Code to let it generate code."
                    echo ""
                    echo "EXPECTED OUTPUT: Generated code snippets or suggested file modifications."
                    echo "ACTION REQUIRED: Copy ALL of Claude Code's output."
                    echo "Save Claude Code's output to a new file in '$plan_dir/' (e.g., 'generated_code_component_X.md')."
                    echo "Then, manually integrate this code into your project."
                    echo ""
                    read -p "Press Enter once you have completed this step."
                    ;;
                b|B)
                    # --- Unit Tester Agent ---
                    echo ""
                    echo "--- Engaging Unit Tester Agent ---"
                    echo "ACTION REQUIRED: Open Claude Code in your terminal."
                    echo "1. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/unit_tester_agent_system_prompt.md' into Claude Code."
                    echo "2. PASTE THE CODE YOU WANT TO TEST (or refer to a specific file in your project) and relevant sections of '$FINAL_PLAN_FILE' into Claude Code."
                    echo "3. Add any specific instructions for the unit tester (e.g., 'Generate Jest tests for the `AuthService.js` module.')."
                    echo "4. Press Enter in Claude Code to let it generate unit tests."
                    echo ""
                    echo "EXPECTED OUTPUT: Generated unit test code."
                    echo "ACTION REQUIRED: Copy ALL of Claude Code's output."
                    echo "Save Claude Code's output to a new file in '$plan_dir/' (e.g., 'generated_tests_component_X.md')."
                    echo "Then, manually integrate and run these tests in your project."
                    echo ""
                    read -p "Press Enter once you have completed this step."
                    ;;
                c|C)
                    # --- Debugger Agent ---
                    echo ""
                    echo "--- Engaging Debugger Agent ---"
                    echo "ACTION REQUIRED: Open Claude Code in your terminal."
                    echo "1. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/debugger_agent_system_prompt.md' into Claude Code."
                    echo "2. PASTE THE ERROR MESSAGE, LOGS, and RELEVANT CODE SNIPPETS into Claude Code."
                    echo "3. Describe the problem you are experiencing."
                    echo "4. Press Enter in Claude Code to let it analyze."
                    echo ""
                    echo "EXPECTED OUTPUT: Analysis of the root cause and proposed solutions."
                    echo "ACTION REQUIRED: Copy ALL of Claude Code's output."
                    echo "Save Claude Code's output to a new file in '$plan_dir/' (e.g., 'debug_report_issue_Y.md')."
                    echo "Then, manually apply any suggested fixes and verify."
                    echo ""
                    read -p "Press Enter once you have completed this step."
                    ;;
                d|D)
                    # --- Documentation Agent ---
                    echo ""
                    echo "--- Engaging Documentation Agent ---"
                    echo "ACTION REQUIRED: Open Claude Code in your terminal."
                    echo "1. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/documentation_agent_system_prompt.md' into Claude Code."
                    echo "2. PASTE THE CODE, API SPECS, or RELEVANT SECTIONS OF '$FINAL_PLAN_FILE' that you want documented into Claude Code."
                    echo "3. Specify the type of documentation needed (e.g., 'Generate JSDoc comments for `AuthService.js`', 'Create an API guide for the user management endpoints')."
                    echo "4. Press Enter in Claude Code to let it generate documentation."
                    echo ""
                    echo "EXPECTED OUTPUT: Generated documentation text."
                    echo "ACTION REQUIRED: Copy ALL of Claude Code's output."
                    echo "Save Claude Code's output to a new file in '$plan_dir/' (e.g., 'docs_api_endpoints.md')."
                    echo "Then, manually integrate this documentation into your project."
                    echo ""
                    read -p "Press Enter once you have completed this step."
                    ;;
                e|E)
                    # --- Code Review Agent ---
                    echo ""
                    echo "--- Engaging Code Review Agent ---"
                    echo "ACTION REQUIRED: Open Claude Code in your terminal."
                    echo "1. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/code_review_agent_system_prompt.md' into Claude Code."
                    echo "2. PASTE THE CODE YOU WANT REVIEWED (e.g., a function, a file, or a diff) into Claude Code."
                    echo "3. Add any specific context for the review (e.g., 'Review this for security vulnerabilities and adherence to our Python style guide.')."
                    echo "4. Press Enter in Claude Code to let it generate the review."
                    echo ""
                    echo "EXPECTED OUTPUT: A structured code review report with suggestions."
                    echo "ACTION REQUIRED: Copy ALL of Claude Code's output."
                    echo "Save Claude Code's output to a new file in '$plan_dir/' (e.g., 'code_review_report_component_X.md')."
                    echo "Then, manually apply suggested improvements."
                    echo ""
                    read -p "Press Enter once you have completed this step."
                    ;;
                f|F)
                    # --- Refactor Agent ---
                    echo ""
                    echo "--- Engaging Refactor Agent ---"
                    echo "ACTION REQUIRED: Open Claude Code in your terminal."
                    echo "1. PASTE THE ENTIRE CONTENTS of '$TEMPLATES_DIR/refactor_agent_system_prompt.md' into Claude Code."
                    echo "2. PASTE THE CODE YOU WANT REFACTORED/OPTIMIZED into Claude Code."
                    echo "3. Add any specific instructions for refactoring (e.g., 'Refactor this function to improve readability and apply the Factory pattern.')."
                    echo "4. Press Enter in Claude Code to let it generate the refactored code."
                    echo ""
                    echo "EXPECTED OUTPUT: Refactored/optimized code with explanations."
                    echo "ACTION REQUIRED: Copy ALL of Claude Code's output."
                    echo "Save Claude Code's output to a new file in '$plan_dir/' (e.g., 'refactored_component_X.md')."
                    echo "Then, manually integrate the refactored code and verify functionality."
                    echo ""
                    read -p "Press Enter once you have completed this step."
                    ;;
                m|M)
                    echo "Returning to Main Menu."
                    break # Exit the inner while loop to return to the main menu
                    ;;
                q|Q)
                    echo "Exiting AI Rails. Goodbye!"
                    exit 0
                    ;;
                *)
                    echo "Invalid choice. Please enter A, B, C, D, E, F, M, or Q."
                    ;;
            esac
            echo ""
        done
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
echo "AI Rails: Workflow complete for this phase."
echo "Refer to your generated plan in the 'output' directory."
echo "-----------------------------------------"