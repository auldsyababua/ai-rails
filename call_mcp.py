import json
import requests
import os

# --- Configuration ---
# Base URLs for your MCPs and n8n
# These should match the IPs/ports configured on your AI Workhorse or NAS
MCP_BASE_URLS = {
    "CodebaseSummaryMCP": "http://10.0.0.2:8003", # Example for CodebaseSummaryMCP
    "SecretsMCP": "http://10.0.0.2:8004",         # Example for SecretsMCP
    # Add other MCPs here as they are implemented
}
N8N_WEBHOOK_BASE_URL = "http://192.168.1.3:80/n8n/webhook/" # Your n8n webhook base URL

# --- Main Function to Call MCPs/n8n ---
def call_mcp(tool_name: str, parameters: dict) -> dict:
    """
    Routes and executes calls to various MCPs or n8n workflows based on the tool_name.

    Args:
        tool_name (str): The name of the tool to call (e.g., "CodebaseSummaryMCP", "SecretsMCP", "n8n_automation").
        parameters (dict): A dictionary of parameters to send to the tool.

    Returns:
        dict: The JSON response from the MCP/n8n, or an error dictionary.
    """
    print(f"Attempting to call tool: {tool_name} with parameters: {parameters}")

    if tool_name == "CodebaseSummaryMCP":
        mcp_url = MCP_BASE_URLS.get("CodebaseSummaryMCP")
        if not mcp_url:
            return {"status": "error", "message": "CodebaseSummaryMCP URL not configured."}
        endpoint = f"{mcp_url}/query" # Assuming a /query endpoint for summary
        try:
            response = requests.post(endpoint, json=parameters, timeout=60)
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"CodebaseSummaryMCP call failed: {e}"}

    elif tool_name == "SecretsMCP":
        mcp_url = MCP_BASE_URLS.get("SecretsMCP")
        if not mcp_url:
            return {"status": "error", "message": "SecretsMCP URL not configured."}
        secret_name = parameters.get("secret_name")
        if not secret_name:
            return {"status": "error", "message": "SecretsMCP requires 'secret_name' parameter."}
        endpoint = f"{mcp_url}/get_secret" # Assuming a /get_secret endpoint
        try:
            response = requests.post(endpoint, json={"secret_name": secret_name}, timeout=30)
            response.raise_for_status()
            # For security, you might want to log that a secret was *requested* but not its value
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"SecretsMCP call failed: {e}"}

    elif tool_name == "n8n_automation":
        workflow_name = parameters.get("workflow_name")
        data = parameters.get("data", {})
        if not workflow_name:
            return {"status": "error", "message": "n8n_automation requires 'workflow_name' parameter."}
        
        # n8n webhooks often have a specific path after the base URL
        # For example: http://192.168.1.3:80/n8n/webhook/your-workflow-name
        n8n_full_webhook_url = f"{N8N_WEBHOOK_BASE_URL}{workflow_name}"
        
        try:
            print(f"Triggering n8n workflow at: {n8n_full_webhook_url}")
            response = requests.post(n8n_full_webhook_url, json=data, timeout=90)
            response.raise_for_status()
            return {"status": "success", "message": f"n8n workflow '{workflow_name}' triggered successfully.", "n8n_response": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"n8n automation call failed: {e}"}

    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

# --- Example Usage (for testing purposes, will be removed when integrated into backend) ---
if __name__ == "__main__":
    # Example: Call CodebaseSummaryMCP
    print("--- Testing CodebaseSummaryMCP ---")
    summary_params = {
        "query": "Summarize the main project structure in the 'templates' directory.",
        "path": "templates"
    }
    summary_result = call_mcp("CodebaseSummaryMCP", summary_params)
    print(json.dumps(summary_result, indent=2))

    print("\n--- Testing SecretsMCP (example with a dummy secret) ---")
    secrets_params = {
        "secret_name": "TEST_API_KEY" # This would be a secret you configure on your Workhorse
    }
    secrets_result = call_mcp("SecretsMCP", secrets_params)
    print(json.dumps(secrets_result, indent=2))

    print("\n--- Testing n8n_automation (example with a dummy workflow) ---")
    n8n_params = {
        "workflow_name": "my-test-workflow", # Replace with an actual n8n workflow webhook path/ID
        "data": {
            "project": "ai-rails",
            "task": "test_automation"
        }
    }
    n8n_result = call_mcp("n8n_automation", n8n_params)
    print(json.dumps(n8n_result, indent=2))

    print("\n--- Testing Unknown Tool ---")
    unknown_result = call_mcp("NonExistentTool", {})
    print(json.dumps(unknown_result, indent=2))