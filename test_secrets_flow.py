#!/usr/bin/env python3
"""Test script for SecretsMCP integration with AI Rails"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
env_file = Path(__file__).parent / ".ai-rails" / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"❌ Environment file not found: {env_file}")
    sys.exit(1)

# Import the call_mcp function
from call_mcp import call_mcp

def test_secret_retrieval():
    """Test retrieving a non-sensitive secret"""
    print("\n=== Testing Non-Sensitive Secret Retrieval ===")
    
    # Test retrieving a non-sensitive secret
    result = call_mcp("SecretsMCP", {"secret_name": "DEFAULT_N8N_WEBHOOK_URL"})
    
    if result.get("status") == "success":
        print(f"✅ Successfully retrieved secret: {result.get('secret_name')}")
        print(f"   Value: {result.get('value')}")
    else:
        print(f"❌ Failed to retrieve secret: {result.get('message')}")
        
    return result

def test_sensitive_secret():
    """Test retrieving a sensitive secret (would require human approval in real flow)"""
    print("\n=== Testing Sensitive Secret Retrieval ===")
    print("Note: In the actual AI Rails flow, this would prompt for human approval")
    
    # Test retrieving a sensitive secret
    result = call_mcp("SecretsMCP", {"secret_name": "ANTHROPIC_API_KEY"})
    
    if result.get("status") == "success":
        print(f"✅ Successfully retrieved sensitive secret: {result.get('secret_name')}")
        # Don't print the actual value for security
        print(f"   Value: [REDACTED - {len(result.get('value', ''))} characters]")
    else:
        print(f"❌ Failed to retrieve secret: {result.get('message')}")
        
    return result

def test_nonexistent_secret():
    """Test retrieving a non-existent secret"""
    print("\n=== Testing Non-Existent Secret ===")
    
    result = call_mcp("SecretsMCP", {"secret_name": "NONEXISTENT_SECRET"})
    
    if result.get("status") == "error":
        print(f"✅ Correctly handled non-existent secret")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"❌ Unexpected result for non-existent secret")
        
    return result

def test_invalid_auth():
    """Test with invalid authentication (by temporarily changing the token)"""
    print("\n=== Testing Invalid Authentication ===")
    
    # Save original token
    original_token = os.environ.get("AI_RAILS_SECRETS_MCP_AUTH_TOKEN")
    
    # Set invalid token
    os.environ["AI_RAILS_SECRETS_MCP_AUTH_TOKEN"] = "invalid-token"
    
    result = call_mcp("SecretsMCP", {"secret_name": "DEFAULT_N8N_WEBHOOK_URL"})
    
    # Restore original token
    if original_token:
        os.environ["AI_RAILS_SECRETS_MCP_AUTH_TOKEN"] = original_token
    
    if result.get("status") == "error" and "401" in str(result.get("details", "")):
        print(f"✅ Authentication correctly rejected invalid token")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"❌ Unexpected result for invalid auth")
        
    return result

if __name__ == "__main__":
    print("=== SecretsMCP Integration Test ===")
    print(f"SecretsMCP URL: {os.getenv('SECRETS_MCP_URL')}")
    print(f"Auth Token: {'SET' if os.getenv('AI_RAILS_SECRETS_MCP_AUTH_TOKEN') else 'NOT SET'}")
    
    # Run tests
    test_secret_retrieval()
    test_sensitive_secret()
    test_nonexistent_secret()
    test_invalid_auth()
    
    print("\n=== Test Complete ===")