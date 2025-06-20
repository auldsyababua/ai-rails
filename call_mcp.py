import json
import requests
import os
import sys
from datetime import datetime

# --- Configuration Section: Centralized URL Management ---
# This section defines the base URLs for your various MCP (Model Context Provider)
# servers and the n8n webhook endpoint.
# These URLs are crucial for the ai_rails_backend.py script to communicate
# with your self-hosted services running on your AI Workhorse or NAS.
#
# IMPORTANT: These values should primarily be set as environment variables
# in your local .env file (for the ai-rails project on your Mac Mini)
# or directly on the system/container where ai_rails_backend.py is run.
# Default values are provided here for development convenience, but for
# production or persistent setup, rely on environment variables.

# URL for your Codebase Summary MCP service.
# This MCP provides context about your project's code.
CODEBASE_SUMMARY_MCP_URL = os.getenv("CODEBASE_SUMMARY_MCP_URL", "http://10.0.0.2:8003")

# URL for your Secrets MCP service.
# This MCP securely manages and serves environment variables/API keys.
SECRETS_MCP_URL = os.getenv("SECRETS_MCP_URL", "http://10.0.0.2:8004")

# URL for your MCP-Sequential-Thinking service.
# This MCP helps agents with structured reasoning and task breakdown.
MCP_SEQUENTIAL_THINKING_URL = os.getenv("MCP_SEQUENTIAL_THINKING_URL", "http://10.0.0.2:8001") # Example default

# URL for your Context7 service.
# This MCP provides vector-database backed context retrieval for documentation.
CONTEXT7_URL = os.getenv("CONTEXT7_URL", "http://10.0.0.2:8002") # Example default

# URL for a Brave Search or similar Web Search MCP.
# This MCP allows agents to perform web searches for external information.
BRAVE_SEARCH_MCP_URL = os.getenv("BRAVE_SEARCH_MCP_URL", "http://10.0.0.2:8005") # Example default

# Base URL for triggering your n8n workflows.
# This should point to the webhook endpoint exposed by your n8n instance,
# likely routed through your Nginx Proxy Manager.
N8N_WEBHOOK_BASE_URL = os.getenv("N8N_WEBHOOK_BASE_URL", "http://192.168.1.3:80/n8n/webhook/")

# Consolidated dictionary for easier lookup within the call_mcp function
MCP_BASE_URLS = {
    "CodebaseSummaryMCP": CODEBASE_SUMMARY_MCP_URL,
    "SecretsMCP": SECRETS_MCP_URL,
    "MCP_Sequential_Thinking": MCP_SEQUENTIAL_THINKING_URL,
    "Context7": CONTEXT7_URL,
    "BraveSearchMCP": BRAVE_SEARCH_MCP_URL,
    "n8n_automation": N8N_WEBHOOK_BASE_URL # n8n is handled separately but included for completeness
}

# --- Core Function: Routing and Executing Tool Calls ---
def call_mcp(tool_name: str, parameters: dict) -> dict:
    """
    Routes and executes calls to various MCPs or n8n workflows based on the tool_name.
    This function acts as a central dispatcher. It receives a tool request from an AI agent
    (after human approval), identifies the target MCP, and makes the appropriate HTTP call.

    Args:
        tool_name (str): The name of the tool to call, as defined in the MCP's JSON definition.
                         (e.g., "CodebaseSummaryMCP", "SecretsMCP", "n8n_automation", etc.)
        parameters (dict): A dictionary of parameters (payload) to send to the tool.
                           The structure of these parameters must match the 'request_schema'
                           defined in the MCP's JSON definition.

    Returns:
        dict: The JSON response received from the MCP/n8n service.
              This response is then typically fed back to the requesting AI agent
              as additional context for its next turn.
              Includes 'status' and 'message' keys for clear error reporting.
    """
    print(f"\n[call_mcp]: Attempting to call tool: {tool_name} with parameters: {json.dumps(parameters, indent=2)}")

    # --- Codebase Summary MCP ---
    if tool_name == "CodebaseSummaryMCP":
        mcp_url = MCP_BASE_URLS.get("CodebaseSummaryMCP")
        if not mcp_url:
            return {"status": "error", "message": "CodebaseSummaryMCP URL not configured in environment variables."}
        
        # Assuming the Codebase Summary MCP has a /query endpoint for requests
        endpoint = f"{mcp_url}/query" 
        try:
            response = requests.post(endpoint, json=parameters, timeout=60) # 60 sec timeout for potentially large queries
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            # Catching various request-related errors (connection, timeout, HTTP errors)
            return {"status": "error", "message": f"CodebaseSummaryMCP call failed: {e}", "details": str(e)}

    # --- Secrets MCP ---
    elif tool_name == "SecretsMCP":
        mcp_url = MCP_BASE_URLS.get("SecretsMCP")
        if not mcp_url:
            return {"status": "error", "message": "SecretsMCP URL not configured in environment variables."}
        
        secret_name = parameters.get("secret_name")
        if not secret_name:
            return {"status": "error", "message": "SecretsMCP requires 'secret_name' parameter in its request."}
        
        # Get project context if available
        project_name = parameters.get("project_name") or os.getenv("AI_RAILS_PROJECT_NAME")
        
        # Get authentication token
        auth_token = os.getenv("AI_RAILS_SECRETS_MCP_AUTH_TOKEN")
        if not auth_token:
            return {"status": "error", "message": "SecretsMCP authentication token not configured in environment variables."}
        
        # Prepare headers with authentication
        headers = {
            "X-API-Key": auth_token,
            "Content-Type": "application/json"
        }
        
        # Build request payload
        request_payload = {"secret_name": secret_name}
        if project_name:
            request_payload["project_name"] = project_name
            print(f"[call_mcp]: Using project context: {project_name}")
        
        # Assuming the Secrets MCP has a /get_secret endpoint
        endpoint = f"{mcp_url}/get_secret"
        try:
            response = requests.post(endpoint, json=request_payload, headers=headers, timeout=30)
            response.raise_for_status()
            # For security, the actual secret value should NOT be logged directly here or elsewhere
            # Only log that a request was made and its status.
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"SecretsMCP call failed: {e}", "details": str(e)}

    # --- MCP-Sequential-Thinking ---
    elif tool_name == "MCP_Sequential_Thinking":
        mcp_url = MCP_BASE_URLS.get("MCP_Sequential_Thinking")
        if not mcp_url:
            return {"status": "error", "message": "MCP_Sequential_Thinking URL not configured in environment variables."}
        
        # Assuming a common endpoint for this type of MCP, e.g., /think or /process
        endpoint = f"{mcp_url}/process" 
        try:
            response = requests.post(endpoint, json=parameters, timeout=90)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"MCP_Sequential_Thinking call failed: {e}", "details": str(e)}

    # --- Context7 MCP ---
    elif tool_name == "Context7":
        mcp_url = MCP_BASE_URLS.get("Context7")
        if not mcp_url:
            return {"status": "error", "message": "Context7 URL not configured in environment variables."}
        
        # Assuming a /query or /context endpoint for retrieval
        endpoint = f"{mcp_url}/query" 
        try:
            response = requests.post(endpoint, json=parameters, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Context7 call failed: {e}", "details": str(e)}

    # --- Brave Search MCP (or similar web search) ---
    elif tool_name == "BraveSearchMCP":
        mcp_url = MCP_BASE_URLS.get("BraveSearchMCP")
        if not mcp_url:
            return {"status": "error", "message": "BraveSearchMCP URL not configured in environment variables."}
        
        # Assuming a /search endpoint
        endpoint = f"{mcp_url}/search" 
        try:
            response = requests.post(endpoint, json=parameters, timeout=120) # Longer timeout for web searches
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"BraveSearchMCP call failed: {e}", "details": str(e)}

    # --- n8n Automation Engine ---
    elif tool_name == "n8n_automation":
        # For n8n, the 'workflow_name' parameter becomes part of the URL path
        # after the base webhook URL.
        n8n_base_url = MCP_BASE_URLS.get("n8n_automation")
        if not n8n_base_url:
            return {"status": "error", "message": "n8n_automation base URL not configured in environment variables."}
        
        workflow_name = parameters.get("workflow_name")
        data_payload = parameters.get("data", {}) # The data to send to the n8n webhook

        if not workflow_name:
            return {"status": "error", "message": "n8n_automation requires 'workflow_name' parameter."}
        
        # Construct the full n8n webhook URL
        # Example: http://192.168.1.3:80/n8n/webhook/my-specific-workflow-name
        n8n_full_webhook_url = f"{n8n_base_url}{workflow_name}"
        
        try:
            print(f"[call_mcp]: Triggering n8n workflow at: {n8n_full_webhook_url}")
            response = requests.post(n8n_full_webhook_url, json=data_payload, timeout=90)
            response.raise_for_status()
            return {"status": "success", "message": f"n8n workflow '{workflow_name}' triggered successfully.", "n8n_response": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"n8n automation call failed: {e}", "details": str(e)}

    # --- Handle Unknown Tools ---
    else:
        # If the requested tool_name does not match any known MCPs, return an error.
        # This prevents agents from attempting to call non-existent services.
        return {"status": "error", "message": f"Unknown tool requested by agent: '{tool_name}'"}

# --- Example Usage (for direct script testing - not used in normal AI Rails flow) ---
if __name__ == "__main__":
    # This block allows you to test the call_mcp function directly from your terminal.
    # It simulates a tool request without needing the full AI Rails backend.
    # To run these tests, ensure you have set the necessary environment variables
    # (e.g., in a .env file loaded by 'python-dotenv' if running this directly).

    print("--- Testing CodebaseSummaryMCP ---")
    summary_params = {
        "query": "Summarize the main project structure in the 'templates' directory.",
        "path": "templates"
    }
    # Note: This will likely fail if CODEBASE_SUMMARY_MCP_URL is not actually running.
    summary_result = call_mcp("CodebaseSummaryMCP", summary_params)
    print(json.dumps(summary_result, indent=2))

    print("\n--- Testing SecretsMCP (example with a dummy secret) ---")
    secrets_params = {
        "secret_name": "TEST_API_KEY" # This would be a secret you configure on your Workhorse
    }
    # Note: This will likely fail if SECRETS_MCP_URL is not actually running.
    secrets_result = call_mcp("SecretsMCP", secrets_params)
    print(json.dumps(secrets_result, indent=2))

    print("\n--- Testing n8n_automation (example with a dummy workflow) ---")
    n8n_params = {
        "workflow_name": "my-test-workflow", # Replace with an actual n8n workflow webhook path/ID
        "data": {
            "project": "ai-rails-test",
            "task": "simulated_automation_trigger"
        }
    }
    # Note: This will likely fail if N8N_WEBHOOK_BASE_URL is not correct/workflow not active.
    n8n_result = call_mcp("n8n_automation", n8n_params)
    print(json.dumps(n8n_result, indent=2))

    print("\n--- Testing Unknown Tool ---")
    unknown_result = call_mcp("NonExistentTool", {})
    print(json.dumps(unknown_result, indent=2))

    print("\n--- Testing MCP_Sequential_Thinking ---")
    seq_think_params = {
        "problem_statement": "How to break down project planning into agile sprints?",
        "context": "We use Scrum with 2-week sprints."
    }
    seq_think_result = call_mcp("MCP_Sequential_Thinking", seq_think_params)
    print(json.dumps(seq_think_result, indent=2))

    print("\n--- Testing Context7 ---")
    context7_params = {
        "query": "What are the latest stable versions of React and Node.js?",
        "source_docs": ["react_official_docs", "nodejs_release_notes"]
    }
    context7_result = call_mcp("Context7", context7_params)
    print(json.dumps(context7_result, indent=2))

    print("\n--- Testing BraveSearchMCP ---")
    brave_search_params = {
        "search_query": "common issues with React and Node.js authentication",
        "num_results": 5
    }
    brave_search_result = call_mcp("BraveSearchMCP", brave_search_params)
    print(json.dumps(brave_search_result, indent=2))