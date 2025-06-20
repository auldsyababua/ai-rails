# Developing Custom MCPs for AI Rails

This guide helps you create custom Model Context Provider (MCP) services that integrate seamlessly with AI Rails.

## MCP Interface Requirements

All MCPs must:
1. Expose HTTP REST endpoints
2. Return JSON responses
3. Handle authentication (if required)
4. Follow our request/response schemas
5. Provide a health check endpoint

## Core MCP Structure

### 1. Basic MCP Template

```python
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from typing import Optional

app = FastAPI(title="Custom MCP Service")

# Configuration
API_KEY = os.getenv("MCP_API_KEY", "default-key")

# Request/Response Models
class BaseRequest(BaseModel):
    """Base request model - extend as needed"""
    pass

class BaseResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[dict] = None

# Authentication
async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "custom-mcp"}

@app.post("/query")
async def process_query(
    request: BaseRequest,
    authenticated: bool = Depends(verify_api_key)
):
    # Your implementation here
    return BaseResponse(
        status="success",
        data={"result": "processed"}
    )
```

### 2. Example: SecretsMCP Implementation

```python
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import os
from typing import Optional
from dotenv import load_dotenv

app = FastAPI(title="Secrets MCP")

# Load environment variables
load_dotenv("/opt/secrets/.env")

# Configuration
SECRETS_MCP_AUTH_KEY = os.getenv("SECRETS_MCP_AUTH_KEY", "change-me")

class SecretRequest(BaseModel):
    secret_name: str

class SecretResponse(BaseModel):
    secret_name: str
    value: Optional[str] = None
    status: str
    message: Optional[str] = None

async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != SECRETS_MCP_AUTH_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or missing API key"
        )
    return True

@app.post("/get_secret", response_model=SecretResponse)
async def get_secret(
    request: SecretRequest,
    authenticated: bool = Depends(verify_api_key)
):
    secret_value = os.getenv(request.secret_name)
    
    if secret_value:
        return SecretResponse(
            secret_name=request.secret_name,
            value=secret_value,
            status="success"
        )
    else:
        return SecretResponse(
            secret_name=request.secret_name,
            status="error",
            message=f"Secret '{request.secret_name}' not found"
        )
```

## MCP Definition Schema

Create a JSON definition file for your MCP in `templates/mcp_definitions/`:

```json
{
  "tool_name": "YourCustomMCP",
  "description": "Brief description of what your MCP does",
  "api_endpoint": "http://localhost:8006",
  "request_schema": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "Description of parameter 1"
      },
      "param2": {
        "type": "number",
        "description": "Description of parameter 2"
      }
    },
    "required": ["param1"]
  },
  "response_format": "Description of the response format",
  "access_control": {
    "Planning Agent": true,
    "Coder Agent": true,
    "Debugger Agent": false
  },
  "agent_specific_guidance": {
    "Planning Agent": "Use this MCP when you need to...",
    "Coder Agent": "This MCP helps with..."
  }
}
```

## Deployment Options

### 1. Docker Container (Recommended)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create a `docker-compose.yml`:
```yaml
version: '3.8'
services:
  your-mcp:
    build: .
    ports:
      - "8006:8000"
    environment:
      - MCP_API_KEY=${MCP_API_KEY}
    volumes:
      - ./secrets:/opt/secrets:ro
    restart: unless-stopped
```

### 2. Systemd Service

Create `/etc/systemd/system/your-mcp.service`:
```ini
[Unit]
Description=Your Custom MCP Service
After=network.target

[Service]
Type=simple
User=mcp-user
WorkingDirectory=/opt/your-mcp
Environment="PATH=/opt/your-mcp/venv/bin"
ExecStart=/opt/your-mcp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8006
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 3. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: your-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: your-mcp
  template:
    metadata:
      labels:
        app: your-mcp
    spec:
      containers:
      - name: your-mcp
        image: your-registry/your-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: MCP_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: api-key
```

## Integration with AI Rails

### 1. Update call_mcp.py

Add your MCP to the routing logic:

```python
# Add to MCP_BASE_URLS dictionary
"YourCustomMCP": os.getenv("YOUR_CUSTOM_MCP_URL", "http://localhost:8006")

# Add routing logic
elif tool_name == "YourCustomMCP":
    mcp_url = MCP_BASE_URLS.get("YourCustomMCP")
    if not mcp_url:
        return {"status": "error", "message": "YourCustomMCP URL not configured"}
    
    endpoint = f"{mcp_url}/your-endpoint"
    try:
        response = requests.post(endpoint, json=parameters, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"YourCustomMCP call failed: {e}"}
```

### 2. Test Your MCP

Create a test script:
```python
import requests
import json

# Test health check
health_response = requests.get("http://localhost:8006/health")
print(f"Health check: {health_response.json()}")

# Test your endpoint
test_payload = {
    "param1": "test value",
    "param2": 123
}

headers = {
    "X-API-Key": "your-test-key",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8006/query",
    json=test_payload,
    headers=headers
)

print(f"Response: {json.dumps(response.json(), indent=2)}")
```

## Best Practices

1. **Error Handling**: Always return structured error responses
2. **Logging**: Implement comprehensive logging for debugging
3. **Validation**: Use Pydantic models for request/response validation
4. **Documentation**: Include OpenAPI/Swagger documentation
5. **Testing**: Write unit and integration tests
6. **Security**: Implement proper authentication and input validation
7. **Performance**: Add caching where appropriate
8. **Monitoring**: Include metrics and health endpoints

## Common Patterns

### Caching Results
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_result(query_hash: str):
    # Expensive operation here
    pass

@app.post("/query")
async def process_query(request: QueryRequest):
    query_hash = hashlib.md5(
        json.dumps(request.dict(), sort_keys=True).encode()
    ).hexdigest()
    
    result = get_cached_result(query_hash)
    return {"status": "success", "data": result}
```

### Async Operations
```python
import asyncio
import aiohttp

async def fetch_external_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@app.post("/async-query")
async def async_query(request: QueryRequest):
    tasks = [fetch_external_data(url) for url in request.urls]
    results = await asyncio.gather(*tasks)
    return {"status": "success", "data": results}
```

## Troubleshooting

1. **Connection Refused**: Check if the service is running and ports are correct
2. **Authentication Errors**: Verify API keys match between client and server
3. **Timeout Issues**: Increase timeout values for long-running operations
4. **CORS Issues**: Configure CORS middleware if accessing from web browsers
5. **Memory Issues**: Implement pagination for large responses

## Next Steps

1. Choose your MCP type and functionality
2. Implement using the templates above
3. Create the MCP definition JSON
4. Deploy using your preferred method
5. Test integration with AI Rails
6. Submit to the community repository!