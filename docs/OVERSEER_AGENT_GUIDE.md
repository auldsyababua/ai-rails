# Overseer Agent Guide

## Overview

The Overseer Agent is a specialized safety component in the AI Rails system that monitors other agents for anomalies, safety violations, and potential issues. It operates independently and cannot be influenced by other agents' outputs.

## Key Features

### 1. Continuous Monitoring
- Reviews agent outputs for boundary violations
- Detects potential security risks in proposed code
- Identifies hallucinations and factual errors
- Monitors for inefficient or stuck workflows

### 2. Alert System
The Overseer uses a three-tier alert system:

- **INFO**: Minor inconsistencies or optimization suggestions
- **WARNING**: Issues requiring human review but not blocking
- **CRITICAL**: Immediate safety concerns that pause the workflow

### 3. Independence
- Runs on a separate LLM instance (preferably Claude for better analysis)
- Cannot be influenced by other agents
- Has read-only access to logs and outputs
- Cannot execute any actions directly

## How It Works

### Automatic Invocation
By default, the Overseer is automatically invoked every 5 agent interactions during the execution phase. This interval can be configured.

### Manual Invocation
Users can manually trigger an Overseer review at any time by selecting option "H" from the execution menu.

### Review Process
1. Collects recent log entries (last 50 for the session)
2. Gathers recent agent outputs (last 5 files)
3. Analyzes for anomalies using predefined criteria
4. Generates structured alerts if issues are found
5. Pauses workflow for CRITICAL alerts

## Alert Format

```
OVERSEER ALERT
--------------
Severity: [INFO|WARNING|CRITICAL]
Agent: [Agent Name]
Timestamp: [ISO 8601 timestamp]
Issue Type: [Boundary Violation|Security Risk|Quality Issue|Other]

Description:
[Detailed description of the issue]

Evidence:
[Specific quotes or references from the agent's output]

Recommendation:
[Suggested action for the human operator]

Risk Assessment:
[Potential impact if not addressed]
```

## Configuration

### Environment Variables
No specific environment variables required, but the Overseer benefits from:
- Higher token limits for comprehensive analysis
- Access to more capable models (Claude recommended)

### Customization Options
In `ai_rails_backend.py`, you can adjust:
- `overseer_check_interval`: Number of interactions between automatic checks
- Alert sensitivity thresholds
- Log entry and output file limits

## Common Anomalies Detected

### 1. Boundary Violations
- Agents attempting actions outside their defined scope
- Requests for tools they shouldn't have access to
- Attempts to modify system files

### 2. Security Risks
- Dangerous commands (e.g., `sudo rm -rf`)
- Exposed credentials in code
- Insecure coding patterns

### 3. Hallucinations
- References to non-existent libraries or functions
- Impossible claims (e.g., "200% test coverage")
- Factually incorrect statements

### 4. Workflow Issues
- Agents stuck in loops
- Excessive retries on the same task
- Off-topic responses

## Best Practices

### For Users
1. Review all Overseer alerts promptly
2. Take CRITICAL alerts seriously - they indicate potential safety issues
3. Use manual invocation if you notice suspicious behavior
4. Consider increasing check frequency for sensitive operations

### For Developers
1. Ensure the Overseer has sufficient context (logs and outputs)
2. Keep the Overseer Agent system prompt updated with new patterns
3. Test the Overseer with simulated anomalies regularly
4. Monitor false positive rates and adjust sensitivity

## Testing the Overseer

A test script is provided at `scratch/test_overseer.py` that simulates various anomalies:

```bash
python scratch/test_overseer.py
```

This will:
1. Simulate normal and suspicious agent activities
2. Invoke the Overseer for review
3. Display any alerts generated

## Integration with Future Features

### UI/Dashboard
- Real-time alert notifications
- Historical anomaly trends
- Alert management interface

### Machine Learning
- Pattern learning from confirmed anomalies
- Adaptive threshold adjustment
- Anomaly prediction

### Multi-Model Analysis
- Cross-validation with different LLMs
- Ensemble anomaly detection
- Specialized models for different anomaly types

## Troubleshooting

### No Alerts Generated
- Check that log entries are being written correctly
- Verify agent outputs are saved to the expected directory
- Ensure the Overseer has access to recent activities

### Too Many False Positives
- Review and update the Overseer system prompt
- Adjust sensitivity thresholds
- Add specific examples to the prompt

### Performance Issues
- Reduce the number of log entries analyzed
- Limit output file content size
- Use a more efficient LLM for routine checks

## Security Considerations

1. The Overseer must never have write access to any system
2. Alert contents should be sanitized before display
3. Critical alerts should trigger additional logging
4. Consider rate limiting for manual invocations

## Conclusion

The Overseer Agent is a critical safety component that helps maintain the bounded, human-centric nature of the AI Rails system. Regular monitoring and prompt response to alerts ensure safe and efficient AI-assisted development.