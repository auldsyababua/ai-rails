# Custom MCP Services for AI Rails

AI Rails requires several Model Context Provider (MCP) services to function fully. While you can run AI Rails with limited functionality, for the complete experience you'll need:

## Required MCP Services

### 1. SecretsMCP (Required for API Key Management)
- **Repository**: [github.com/colinaulds/secrets-mcp](https://github.com/colinaulds/secrets-mcp) *(To be published)*
- **Purpose**: Securely manages API keys and environment variables
- **Features**: 
  - Human-in-the-loop approval for sensitive secrets
  - API key authentication
  - Audit logging
  - Docker containerization

### 2. CodebaseSummaryMCP (Recommended)
- **Repository**: [github.com/colinaulds/codebase-summary-mcp](https://github.com/colinaulds/codebase-summary-mcp) *(To be published)*
- **Purpose**: Provides AI agents with project context and code summaries
- **Alternative**: Users can implement their own or use existing code indexing tools

## Setting Up Custom MCPs

Users have three options:

### Option 1: Use Our Reference Implementations
Clone and deploy our MCP implementations:
```bash
# SecretsMCP
git clone https://github.com/colinaulds/secrets-mcp
cd secrets-mcp
docker-compose up -d

# CodebaseSummaryMCP  
git clone https://github.com/colinaulds/codebase-summary-mcp
cd codebase-summary-mcp
docker-compose up -d
```

### Option 2: Create Your Own
Follow our MCP Development Guide (see [`docs/MCP_DEVELOPMENT_GUIDE.md`](MCP_DEVELOPMENT_GUIDE.md)) to create custom implementations that match your infrastructure.

### Option 3: Use Community MCPs
Check our [Community MCPs List](COMMUNITY_MCPS.md) for alternative implementations.

## Quick Start with Docker

We provide a Docker Compose setup that includes mock MCP services for testing:
```bash
docker-compose -f docker/mcp-services.yml up
```

This starts mock services that respond with sample data, allowing you to test the AI Rails workflow without setting up real MCP services.

## Environment Configuration

After deploying your MCPs, update your `.env` file with the appropriate URLs:

```env
# SecretsMCP endpoint
SECRETS_MCP_URL=http://localhost:8004
AI_RAILS_SECRETS_MCP_AUTH_TOKEN=your-auth-token-here

# CodebaseSummaryMCP endpoint  
CODEBASE_SUMMARY_MCP_URL=http://localhost:8003

# Other MCP endpoints as needed
MCP_SEQUENTIAL_THINKING_URL=http://localhost:8001
CONTEXT7_URL=http://localhost:8002
BRAVE_SEARCH_MCP_URL=http://localhost:8005
```

## Security Considerations

1. **SecretsMCP**: Always deploy with authentication enabled
2. **Network Isolation**: Consider running MCPs on a private network
3. **HTTPS**: Use HTTPS for production deployments
4. **Access Control**: Implement proper access controls for sensitive MCPs
5. **Project Isolation**: Use project-scoped secrets for client work (see [Project Secrets Guide](PROJECT_SECRETS_GUIDE.md))

## Troubleshooting

### MCP Connection Issues
1. Verify the service is running: `curl http://localhost:8004/health`
2. Check logs: `docker logs secrets-mcp`
3. Ensure environment variables are set correctly
4. Verify network connectivity between AI Rails and MCP services

### Authentication Failures
1. Ensure `AI_RAILS_SECRETS_MCP_AUTH_TOKEN` matches the token configured in SecretsMCP
2. Check that authentication headers are being sent correctly
3. Review MCP service logs for authentication errors

## Next Steps

- Deploy the required MCP services for your use case
- Configure your environment variables
- Test the connection using the provided test scripts
- Start using AI Rails with full MCP integration!