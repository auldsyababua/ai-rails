**Tool Definition: n8n Automation Engine**

**Purpose:** The n8n Automation Engine is available to set up and manage various automations and integrations (e.g., sending emails, updating spreadsheets, interacting with APIs, scheduling tasks, triggering external services).

**How to Request Automation:**
If an automation task is part of a plan or a solution, formulate a request in the following JSON-like structure. This request should be clear and self-contained, describing the desired n8n workflow. The human operator will then take this request and configure/trigger the n8n workflow.

```json
{
  "tool_name": "n8n_automation_engine",
  "action": "[Describe the specific action or goal for n8n, e.g., 'send email notification', 'update CRM record', 'trigger daily report generation']",
  "details": {
    "workflow_description": "[A detailed description of the n8n workflow needed, including inputs, outputs, conditions, and sequence of nodes.]",
    "required_inputs": {
      "[input_name_1]": "[description_of_input_1]",
      "[input_name_2]": "[description_of_input_2]"
    },
    "expected_outputs": {
      "[output_name_1]": "[description_of_output_1]"
    },
    "notes": "[Any additional notes or considerations for setting up the n8n workflow.]"
  }
}