import os
import json
import requests
from pathlib import Path
from datetime import datetime
import re
import sys

# Assume call_mcp is in the same directory or accessible via PYTHONPATH
from call_mcp import call_mcp

# --- Configuration (Adjust as needed) ---
PROJECT_ROOT = Path(__file__).parent.resolve()
TEMPLATES_DIR = PROJECT_ROOT / "templates"
MCP_DEFINITIONS_DIR = TEMPLATES_DIR / "mcp_definitions"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "log"
LOG_FILE = LOG_DIR / "ai-rails.log"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://10.0.0.2:11434")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY") # Will be retrieved via SecretsMCP

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- Logging Function ---
def log_event(event_type: str, message: str, agent_role: str = "Orchestrator", session_id: str = "default", llm_model: str = "N/A", details: dict = None):
    """Logs an event to the ai-rails.log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "agent_role": agent_role,
        "llm_model_used": llm_model,
        "event_type": event_type,
        "message": message,
        "details": details if details is not None else {}
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    print(f"LOGGED [{agent_role}/{event_type}]: {message}") # Also print to console for immediate feedback

# --- Load MCP Definitions ---
def load_mcp_definitions() -> dict:
    """Loads all MCP definitions from the mcp_definitions directory."""
    mcp_defs = {}
    for mcp_file in MCP_DEFINITIONS_DIR.glob("*.json"):
        try:
            with open(mcp_file, "r") as f:
                definition = json.load(f)
                mcp_defs[definition.get("tool_name")] = definition
        except json.JSONDecodeError as e:
            log_event("ERROR", f"Failed to parse MCP definition {mcp_file.name}: {e}", agent_role="Orchestrator")
        except FileNotFoundError:
            log_event("ERROR", f"MCP definition file not found: {mcp_file.name}", agent_role="Orchestrator")
    return mcp_defs

# --- Dynamic Prompt Builder ---
def build_agent_prompt(agent_template_path: Path, tool_definitions: dict, additional_context: str = "") -> str:
    """
    Reads an agent's system prompt template and dynamically injects tool definitions.
    """
    try:
        with open(agent_template_path, "r") as f:
            template_content = f.read()

        tool_json_str = ""
        if tool_definitions:
            tool_list = []
            for name, definition in tool_definitions.items():
                # Only include tool_name, description, and request_schema
                # Omit api_endpoint and response_format from prompt as agents don't use them directly
                tool_info = {k: v for k, v in definition.items() if k in ["tool_name", "description", "request_schema"]}
                tool_list.append(tool_info)
            tool_json_str = json.dumps(tool_list, indent=2)

        # Replace the placeholder in the template
        full_prompt = template_content.replace(
            "--- TOOL_DEFINITIONS_START ---\n// This section will be dynamically injected by ai_rails_backend.py\n---\n",
            f"--- TOOL_DEFINITIONS_START ---\n{tool_json_str}\n"
        )
        full_prompt = full_prompt.replace(
            "\n--- TOOL_DEFINITIONS_END ---",
            "\n--- TOOL_DEFINITIONS_END ---"
        )
        
        # Append any additional context at the end
        if additional_context:
            full_prompt += f"\n\n--- ADDITIONAL CONTEXT ---\n{additional_context}\n--------------------------"

        return full_prompt
    except FileNotFoundError:
        log_event("ERROR", f"Agent template not found: {agent_template_path}", agent_role="Orchestrator")
        return ""

# --- LLM Interaction Functions ---
def call_ollama(prompt: str, model: str = "qwen2.5-coder:32b") -> str:
    """Calls the local Ollama LLM."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False # We want the full response at once
    }
    log_event("LLM_CALL", f"Calling Ollama model: {model}", llm_model=model, details={"prompt_length": len(prompt)})
    try:
        response = requests.post(url, headers=headers, json=data, timeout=300) # 5 min timeout
        response.raise_for_status()
        result = response.json()
        log_event("LLM_RESPONSE", f"Received response from Ollama: {result.get('done', False)}", llm_model=model, details={"response_length": len(result.get('response', ''))})
        return result.get("response", "")
    except requests.exceptions.RequestException as e:
        log_event("LLM_ERROR", f"Ollama call failed: {e}", llm_model=model)
        print(f"Error calling Ollama: {e}")
        return f"Error: Could not communicate with Ollama. {e}"

def call_claude(prompt: str, model: str = "claude-3-opus-20240229") -> str:
    """Calls the Anthropic Claude API."""
    if not CLAUDE_API_KEY:
        log_event("LLM_ERROR", "Claude API Key not set. Cannot call Claude.", llm_model=model)
        return "Error: Claude API Key is not configured."

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": 4096, # Adjust as needed
        "messages": [{"role": "user", "content": prompt}]
    }
    log_event("LLM_CALL", f"Calling Claude model: {model}", llm_model=model, details={"prompt_length": len(prompt)})
    try:
        response = requests.post(url, headers=headers, json=data, timeout=300) # 5 min timeout
        response.raise_for_status()
        result = response.json()
        log_event("LLM_RESPONSE", f"Received response from Claude: {result.get('id', 'N/A')}", llm_model=model, details={"response_length": len(result.get('content', [{}])[0].get('text', ''))})
        return result.get("content", [{}])[0].get("text", "")
    except requests.exceptions.RequestException as e:
        log_event("LLM_ERROR", f"Claude call failed: {e}", llm_model=model)
        print(f"Error calling Claude: {e}")
        return f"Error: Could not communicate with Claude API. {e}"

# --- Agent Orchestration Function ---
def engage_agent(
    agent_role: str,
    agent_template_filename: str,
    user_input_content: str,
    project_output_path: Path,
    session_id: str,
    llm_choice: str = "ollama",
    previous_tool_output: str = "" # New parameter for tool output feedback
):
    """
    Engages a specific AI agent with a prompt and handles its output,
    including tool request detection and human gating.
    """
    log_event("AGENT_ENGAGE", f"Engaging {agent_role} agent.", agent_role=agent_role, session_id=session_id)

    agent_template_path = TEMPLATES_DIR / agent_template_filename
    
    # Load all MCP definitions to inject into the agent's prompt
    all_mcp_definitions = load_mcp_definitions()

    # Add previous tool output as additional context
    context_for_agent = user_input_content
    if previous_tool_output:
        context_for_agent += f"\n\n--- PREVIOUS TOOL OUTPUT ---\n{previous_tool_output}\n--------------------------"
        log_event("CONTEXT_INJECTED", "Previous tool output injected into agent prompt.", agent_role=agent_role, session_id=session_id)

    full_prompt = build_agent_prompt(
        agent_template_path,
        all_mcp_definitions,
        additional_context=context_for_agent
    )

    if not full_prompt:
        print("Failed to build agent prompt. Exiting agent engagement.")
        return

    print(f"\n--- Sending prompt to {agent_role} ({llm_choice}) ---")
    # print(f"DEBUG: Full Prompt Content:\n{full_prompt[:500]}...") # Print first 500 chars for debug

    agent_response = ""
    if llm_choice == "ollama":
        agent_response = call_ollama(full_prompt)
    elif llm_choice == "claude":
        agent_response = call_claude(full_prompt)
    else:
        print("Invalid LLM choice.")
        return

    if not agent_response:
        print(f"Agent ({agent_role}) did not return a response.")
        log_event("AGENT_NO_RESPONSE", f"{agent_role} did not return a response.", agent_role=agent_role, session_id=session_id, llm_model=llm_choice)
        return

    # Save the raw agent output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = project_output_path / f"{agent_role.lower().replace(' ', '_')}_output_{timestamp}.md"
    try:
        with open(output_filename, "w") as f:
            f.write(agent_response)
        log_event("AGENT_OUTPUT_SAVED", f"{agent_role} output saved to: {output_filename}", agent_role=agent_role, session_id=session_id, details={"path": str(output_filename)})
        print(f"\n--- {agent_role} Output Saved ---")
        print(f"You can review it at: {output_filename}")
    except IOError as e:
        log_event("ERROR", f"Failed to save agent output: {e}", agent_role=agent_role, session_id=session_id)
        print(f"Error saving agent output: {e}")
        print("\n--- Raw Agent Output ---")
        print(agent_response)


    # --- Tool Request Detection ---
    tool_request_match = re.search(r"```json\s*(.*?)\s*```", agent_response, re.DOTALL)
    if tool_request_match:
        try:
            tool_request_json = json.loads(tool_request_match.group(1))
            if tool_request_json.get("type") == "tool_request":
                tool_name = tool_request_json.get("tool_name")
                parameters = tool_request_json.get("parameters", {})
                explanation = tool_request_json.get("explanation", "No explanation provided.")

                log_event("MCP_REQUEST_FORMULATED", f"Agent formulated tool request for {tool_name}.", 
                          agent_role=agent_role, session_id=session_id, 
                          details={"tool_name": tool_name, "parameters": parameters, "explanation": explanation})
                
                print(f"\n--- !!! HUMAN INTERVENTION REQUIRED !!! ---")
                print(f"The {agent_role} has requested to use a tool:")
                print(f"Tool Name: {tool_name}")
                print(f"Explanation: {explanation}")
                print(f"Raw Request: {json.dumps(parameters, indent=2)}")

                # Get human approval
                confirm = input("Do you approve this tool request? (yes/no): ").lower().strip()
                if confirm == "yes":
                    log_event("HUMAN_DECISION", f"Human approved tool request for {tool_name}.", agent_role="Orchestrator", session_id=session_id)
                    print(f"Executing tool: {tool_name}...")
                    tool_output = call_mcp(tool_name, parameters)
                    log_event("TOOL_EXECUTION_RESULT", f"Tool {tool_name} executed. Status: {tool_output.get('status', 'N/A')}", 
                              agent_role="Orchestrator", session_id=session_id, details=tool_output)
                    
                    print("\n--- Tool Execution Result ---")
                    print(json.dumps(tool_output, indent=2))
                    
                    # Recursively call engage_agent to feed tool output back to the agent
                    print(f"\n--- Re-engaging {agent_role} with tool output ---")
                    engage_agent(
                        agent_role=agent_role,
                        agent_template_filename=agent_template_filename,
                        user_input_content=user_input_content, # Pass original user input
                        project_output_path=project_output_path,
                        session_id=session_id,
                        llm_choice=llm_choice,
                        previous_tool_output=json.dumps(tool_output, indent=2) # Pass tool output
                    )

                else:
                    log_event("HUMAN_DECISION", f"Human denied tool request for {tool_name}.", agent_role="Orchestrator", session_id=session_id)
                    custom_feedback = input("Please provide feedback to the agent (e.g., 'Deny: MCP not available', 'Refine request to...'): ")
                    # Recursively call engage_agent to feed human feedback back
                    print(f"\n--- Re-engaging {agent_role} with human feedback ---")
                    engage_agent(
                        agent_role=agent_role,
                        agent_template_filename=agent_template_filename,
                        user_input_content=user_input_content, # Pass original user input
                        project_output_path=project_output_path,
                        session_id=session_id,
                        llm_choice=llm_choice,
                        previous_tool_output=f"Human Feedback: {custom_feedback}" # Pass human feedback
                    )
            else:
                log_event("AGENT_OUTPUT_JSON_NOT_TOOL_REQUEST", "Agent output contained JSON but not a valid tool_request.", agent_role=agent_role, session_id=session_id, details={"json": tool_request_json})
                print("\nAgent output contained a JSON block, but it was not a recognized 'tool_request'.")
                print("Please review the agent's output manually.")

        except json.JSONDecodeError:
            log_event("AGENT_OUTPUT_INVALID_JSON", "Agent output contained a malformed JSON block.", agent_role=agent_role, session_id=session_id)
            print("\nAgent output contained a JSON-like block, but it was malformed.")
            print("Please review the agent's output manually for parsing errors.")
        except Exception as e:
            log_event("ERROR", f"Error processing agent's tool request: {e}", agent_role=agent_role, session_id=session_id)
            print(f"An unexpected error occurred while processing the agent's output: {e}")
            print("Please review the agent's output manually.")
    else:
        log_event("AGENT_OUTPUT_NO_TOOL_REQUEST", "Agent output did not contain a tool request.", agent_role=agent_role, session_id=session_id)
        print("\n--- No Tool Request Detected in Agent Output ---")
        print("Please review the agent's output and decide the next step manually.")


# --- Main Orchestration Loop (called by run_workflow.sh) ---
def main_workflow_loop(
    project_name: str,
    workflow_type: str, # "new_project" or "feature_update" or "execution"
    plan_path: Path = None # Only for execution phase
):
    session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    log_event("WORKFLOW_START", f"AI Rails workflow started for {project_name} ({workflow_type}).", session_id=session_id)

    current_project_output_dir = OUTPUT_DIR / f"{workflow_type}_plans" / project_name
    current_project_output_dir.mkdir(parents=True, exist_ok=True)

    initial_idea_file = None
    if workflow_type == "new_project":
        initial_idea_file = current_project_output_dir / "initial_project_idea.md"
    elif workflow_type == "feature_update":
        initial_idea_file = current_project_output_dir / "feature_update_idea.md"
    
    # Read initial idea content if available
    user_initial_idea_content = ""
    if initial_idea_file and initial_idea_file.exists():
        with open(initial_idea_file, "r") as f:
            user_initial_idea_content = f.read()

    # For 'execution' phase, we need a base plan to start with
    if workflow_type == "execution" and not plan_path:
        print("Error: Execution phase requires a specified plan path.")
        log_event("ERROR", "Execution phase started without a plan path.", session_id=session_id)
        return

    if workflow_type == "execution" and plan_path.exists():
        with open(plan_path, "r") as f:
            user_initial_idea_content = f.read() # The 'plan' becomes the 'initial idea' for execution agents

    print("\n--- Select LLM for current session ---")
    llm_choice = input("Use Ollama (default) or Claude? (ollama/claude): ").lower().strip()
    if llm_choice not in ["ollama", "claude"]:
        print("Invalid LLM choice. Defaulting to Ollama.")
        llm_choice = "ollama"

    if llm_choice == "claude" and not CLAUDE_API_KEY:
        print("Claude API Key not set. Attempting to retrieve via SecretsMCP.")
        secrets_result = call_mcp("SecretsMCP", {"secret_name": "ANTHROPIC_API_KEY"})
        if secrets_result.get("status") == "success" and secrets_result.get("value"):
            os.environ["ANTHROPIC_API_KEY"] = secrets_result["value"]
            global CLAUDE_API_KEY
            CLAUDE_API_KEY = secrets_result["value"]
            print("Claude API Key successfully retrieved.")
        else:
            print("Failed to retrieve Claude API Key. Falling back to Ollama.")
            llm_choice = "ollama"


    if workflow_type in ["new_project", "feature_update"]:
        # Engage Planning Agent
        engage_agent(
            agent_role="Planning Agent",
            agent_template_filename="planning_agent_system_prompt.md",
            user_input_content=user_initial_idea_content,
            project_output_path=current_project_output_dir,
            session_id=session_id,
            llm_choice=llm_choice
        )
        print(f"\nPlanning session for {project_name} complete. Review output in {current_project_output_dir}")
        print("You can now enter the Execution Phase or refine the plan manually.")

    elif workflow_type == "execution":
        # Loop for execution phase actions
        while True:
            print("\n--- Execution Actions ---")
            print("A) Engage Coder Agent")
            print("B) Engage Unit Tester Agent")
            print("C) Engage Debugger Agent")
            print("D) Engage Documentation Agent")
            print("E) Engage Code Review Agent")
            print("F) Engage Refactor Agent")
            print("G) Engage n8n Flow Creator Agent") # New agent
            print("M) Back to Main Menu")
            print("Q) Quit AI Rails")
            exec_choice = input("Choose an action: ").lower().strip()

            if exec_choice == "a":
                # Coder Agent
                engage_agent(
                    agent_role="Coder Agent",
                    agent_template_filename="coder_agent_system_prompt.md",
                    user_input_content=user_initial_idea_content, # The plan content
                    project_output_path=current_project_output_dir,
                    session_id=session_id,
                    llm_choice=llm_choice
                )
            elif exec_choice == "b":
                # Unit Tester Agent
                engage_agent(
                    agent_role="Unit Tester Agent",
                    agent_template_filename="unit_tester_agent_system_prompt.md",
                    user_input_content=user_initial_idea_content, # The plan content
                    project_output_path=current_project_output_dir,
                    session_id=session_id,
                    llm_choice=llm_choice
                )
            elif exec_choice == "c":
                # Debugger Agent
                engage_agent(
                    agent_role="Debugger Agent",
                    agent_template_filename="debugger_agent_system_prompt.md",
                    user_input_content=user_initial_idea_content, # Context for debugging
                    project_output_path=current_project_output_dir,
                    session_id=session_id,
                    llm_choice=llm_choice
                )
            elif exec_choice == "d":
                # Documentation Agent
                engage_agent(
                    agent_role="Documentation Agent",
                    agent_template_filename="documentation_agent_system_prompt.md",
                    user_input_content=user_initial_idea_content, # Code/plan for docs
                    project_output_path=current_project_output_dir,
                    session_id=session_id,
                    llm_choice=llm_choice
                )
            elif exec_choice == "e":
                # Code Review Agent
                engage_agent(
                    agent_role="Code Review Agent",
                    agent_template_filename="code_review_agent_system_prompt.md",
                    user_input_content=user_initial_idea_content, # Code for review
                    project_output_path=current_project_output_dir,
                    session_id=session_id,
                    llm_choice=llm_choice
                )
            elif exec_choice == "f":
                # Refactor Agent
                engage_agent(
                    agent_role="Refactor Agent",
                    agent_template_filename="refactor_agent_system_prompt.md",
                    user_input_content=user_initial_idea_content, # Code for refactoring
                    project_output_path=current_project_output_dir,
                    session_id=session_id,
                    llm_choice=llm_choice
                )
            elif exec_choice == "g":
                # n8n Flow Creator Agent
                # For this agent, the 'user_input_content' would be the 'n8n Automation Request'
                # For now, let's just use the main plan as input. You might want to
                # prompt the user for a specific n8n automation request here.
                print("\n--- Engaging n8n Flow Creator Agent ---")
                n8n_request_input = input("Please provide a natural language description of the n8n automation you need: ")
                engage_agent(
                    agent_role="n8n Flow Creator Agent",
                    agent_template_filename="n8n_flow_creator_agent_system_prompt.md",
                    user_input_content=n8n_request_input,
                    project_output_path=current_project_output_dir,
                    session_id=session_id,
                    llm_choice=llm_choice
                )

            elif exec_choice == "m":
                log_event("WORKFLOW_STATE_CHANGE", "Returning to Main Menu.", session_id=session_id)
                break
            elif exec_choice == "q":
                log_event("WORKFLOW_END", "AI Rails workflow quit.", session_id=session_id)
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

    log_event("WORKFLOW_END", f"AI Rails workflow ended for {project_name} ({workflow_type}).", session_id=session_id)

if __name__ == "__main__":
    # This block will be used if ai_rails_backend.py is run directly for testing.
    # When integrated with run_workflow.sh, main_workflow_loop will be called directly.
    print("This script is usually called by run_workflow.sh. Running in standalone test mode.")
    # Example: Simulating a new project kickoff
    # main_workflow_loop(project_name="test-project", workflow_type="new_project")

    # Example: Simulating an execution phase
    # Assuming 'my-test-plan.md' exists in output/execution_plans/my-test-project/
    # test_plan_path = OUTPUT_DIR / "execution_plans" / "my-test-project" / "my-test-plan.md"
    # main_workflow_loop(project_name="my-test-project", workflow_type="execution", plan_path=test_plan_path)

    # For now, just a placeholder. The real entry point will be run_workflow.sh
    print("Please use run_workflow.sh to start the AI Rails system.")