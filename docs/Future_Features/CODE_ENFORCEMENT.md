# Future Update Doc - code enforcing outputs with scripts

Enforce proper requests and outputs from each agent using scripts and a "linter-like" mechanism. This is a crucial aspect of building a robust and reliable "AI Rails" system, preventing agents from "hallucinating" incorrect JSON or malformed requests that would break downstream processes.

The `ai_rails_backend.py` script already has the foundation for this with its `re.search(r"```json\s*(.*?)\s*```", agent_response, re.DOTALL)` and `json.loads()` blocks. When an agent outputs a JSON block, the backend attempts to parse it. If it's malformed JSON, `json.JSONDecodeError` is caught.

To extend this to a "linter-like" enforcement, you would enhance this validation process. Here's how:

### **Enforcing Proper Requests and Outputs with Scripts**

1.  **JSON Schema Validation for Tool Requests:**
    * **Mechanism:** When an agent proposes a `tool_request` JSON, the `ai_rails_backend.py` can compare this proposed `parameters` payload against the `request_schema` defined in the corresponding MCP's JSON definition.
    * **Implementation:** You would use a Python library like `jsonschema` to validate the agent's proposed `parameters` dictionary against the `request_schema` that was loaded from the MCP definition.
    * **Action on Failure:** If the validation fails (e.g., a required field is missing, a data type is incorrect, an enum value is invalid), the backend **does not execute the tool**. Instead, it provides specific, structured feedback *to the agent* (via the `previous_tool_output` mechanism) explaining *exactly* what was wrong with the JSON request. This forces the agent to self-correct in the next turn.

2.  **Output Content and Format Validation:**
    * **Mechanism:** For the final output of an agent (e.g., the Coder Agent's code, the n8n Flow Creator Agent's JSON workflow), you can implement post-processing validation steps.
    * **For Coder Agent:** You could use linters (e.g., `flake8` for Python, `ESLint` for JavaScript) or formatters (e.g., `Black` for Python, `Prettier` for JavaScript) on the generated code. If the code doesn't pass, the backend informs the Coder Agent, prompting a retry with correction.
    * **For n8n Flow Creator Agent:** After parsing the agent's output as JSON, you can validate it against a known n8n workflow JSON schema (if one is available, or a simplified custom one).
    * **Action on Failure:** Similar to tool request validation, if the output doesn't meet the required standards, the backend provides detailed feedback to the agent to prompt a revision.

### **Where to Implement This in `ai_rails_backend.py`**

The primary place to implement this enforcement is within the `engage_agent` function, specifically after the `tool_request_match` logic.

**Example Sketch of Enhanced Validation:**

```python
# ... inside engage_agent function, after tool_request_match and json.loads ...

                if tool_request_json.get("type") == "tool_request":
                    tool_name = tool_request_json.get("tool_name")
                    parameters = tool_request_json.get("parameters", {})
                    explanation = tool_request_json.get("explanation", "No explanation provided.")

                    # --- NEW VALIDATION STEP ---
                    mcp_definition = all_mcp_definitions.get(tool_name)
                    if not mcp_definition:
                        validation_feedback = f"Error: Requested tool '{tool_name}' is not defined or accessible."
                        log_event("TOOL_REQUEST_VALIDATION_FAILED", validation_feedback, agent_role=agent_role, session_id=session_id)
                        print(validation_feedback)
                        # Re-engage agent with specific feedback
                        engage_agent(
                            agent_role=agent_role,
                            agent_template_filename=agent_template_filename,
                            user_input_content=user_input_content,
                            project_output_path=project_output_path,
                            session_id=session_id,
                            llm_choice=llm_choice,
                            previous_tool_output=f"Human/System Feedback: Tool request validation failed: {validation_feedback}"
                        )
                        return # Exit current turn, agent gets feedback to retry

                    if "request_schema" in mcp_definition:
                        import jsonschema # You'd need to install this library: pip install jsonschema
                        try:
                            jsonschema.validate(instance=parameters, schema=mcp_definition["request_schema"])
                            # Validation successful
                            log_event("TOOL_REQUEST_VALIDATED", f"Tool request for {tool_name} passed schema validation.", agent_role=agent_role, session_id=session_id)
                        except jsonschema.exceptions.ValidationError as ve:
                            validation_feedback = f"Error: Tool request for '{tool_name}' failed schema validation. Details: {ve.message}. Please correct your JSON parameters."
                            log_event("TOOL_REQUEST_VALIDATION_FAILED", validation_feedback, agent_role=agent_role, session_id=session_id, details={"error": ve.message, "tool_request": tool_request_json})
                            print(validation_feedback)
                            # Re-engage agent with specific feedback to correct its request
                            engage_agent(
                                agent_role=agent_role,
                                agent_template_filename=agent_template_filename,
                                user_input_content=user_input_content,
                                project_output_path=project_output_path,
                                session_id=session_id,
                                llm_choice=llm_choice,
                                previous_tool_output=f"Human/System Feedback: Tool request validation failed: {validation_feedback}"
                            )
                            return # Exit current turn, agent gets feedback to retry
                    # --- END NEW VALIDATION STEP ---

                    # ... rest of the tool execution and human gating logic ...
```

This "linter-like" enforcement is a powerful way to put your agents on tighter "rails" for their outputs, reducing manual intervention and leading to more reliable automated interactions.