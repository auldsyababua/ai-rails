# Community MCP Implementations

This page lists community-contributed MCP implementations that work with AI Rails. 

## Verified Implementations

*None yet - be the first to contribute!*

## Submission Guidelines

Want to share your MCP implementation? Follow these steps:

1. Fork this repository
2. Add your MCP to the appropriate section below
3. Include all required information (see template)
4. Ensure your MCP follows our [Development Guide](MCP_DEVELOPMENT_GUIDE.md)
5. Submit a Pull Request

### Review Criteria

Your MCP submission will be reviewed for:
- Compatibility with AI Rails MCP interface
- Clear documentation and setup instructions
- Proper error handling and response formats
- Security considerations (especially for action-oriented MCPs)

## Template for Submissions

```markdown
### [Your MCP Name]
- **Repository**: [GitHub/GitLab/etc. link]
- **Author**: [Your name/handle]
- **Description**: Brief description of what your MCP does
- **Category**: Knowledge-Based / Action-Oriented / Utility
- **AI Rails Version**: Compatible versions (e.g., 1.0+)
- **Features**: 
  - Key feature 1
  - Key feature 2
  - Key feature 3
- **Requirements**:
  - External services needed
  - API keys required
  - System dependencies
- **Setup**: Link to detailed setup guide
- **Example Usage**: Brief example of how agents use this MCP
- **License**: License type
```

## Knowledge-Based MCPs

These MCPs provide information and context to AI agents without performing actions.

### Example Entry:
```
### WeatherMCP
- **Repository**: github.com/example/weather-mcp
- **Author**: @example
- **Description**: Provides current weather and forecast data
- **Category**: Knowledge-Based
- **AI Rails Version**: 1.0+
- **Features**: 
  - Current weather conditions
  - 7-day forecasts
  - Historical weather data
- **Requirements**:
  - OpenWeatherMap API key
  - Python 3.9+
- **Setup**: See repository README
- **Example Usage**: Agents can query weather for location-based decisions
- **License**: MIT
```

## Action-Oriented MCPs

These MCPs perform actions on behalf of agents (use with caution and proper human approval).

*Note: Action-oriented MCPs should always implement proper authentication and human approval workflows.*

## Utility MCPs

These MCPs provide utility functions like data transformation, validation, or processing.

## Integration Adapters

These implementations adapt existing services to work as AI Rails MCPs.

### Todoist MCP Adapter
- **Repository**: *Example - not yet implemented*
- **Description**: Adapts @abhiz123/todoist-mcp-server for AI Rails
- **Note**: Shows how to wrap existing MCP servers for AI Rails compatibility

## Testing Tools

Tools and utilities for testing MCP implementations.

### MCP Test Suite
- **Repository**: *To be created*
- **Description**: Automated testing suite for MCP compliance
- **Features**:
  - Endpoint validation
  - Response format checking
  - Performance benchmarks

## Contributing

### How to Test Your MCP

Before submitting:
1. Ensure all endpoints return proper JSON responses
2. Test authentication mechanisms
3. Verify error handling returns expected formats
4. Check compatibility with AI Rails' `call_mcp.py`
5. Include example agent interactions

### Community Standards

- Keep your MCP focused on a single responsibility
- Document all environment variables and configuration
- Provide Docker images when possible
- Include security considerations in documentation
- Respond to issues and pull requests promptly

## Resources

- [MCP Development Guide](MCP_DEVELOPMENT_GUIDE.md)
- [AI Rails Architecture](../DEEP-EXPLANATION.md)
- [Custom MCP Setup](CUSTOM_MCP_SETUP.md)

---

*Want to discuss MCP development? Open an issue with the `mcp-discussion` label!*