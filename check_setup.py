#!/usr/bin/env python3
"""
Quick setup verification script
Check if environment is properly configured
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded successfully")
except ImportError:
    print("❌ dotenv not installed")
    sys.exit(1)

# Check environment variables
print("\n🔍 Checking environment variables...")
env_vars = {
    "GOOGLE_ADS_AUTH_TYPE": os.environ.get("GOOGLE_ADS_AUTH_TYPE", "NOT_SET"),
    "GOOGLE_ADS_CREDENTIALS_PATH": os.environ.get("GOOGLE_ADS_CREDENTIALS_PATH", "NOT_SET"),
    "GOOGLE_ADS_DEVELOPER_TOKEN": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "NOT_SET"),
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "NOT_SET"),
}

for key, value in env_vars.items():
    if value == "NOT_SET" or value == "" or "your_" in value or "/path/to/" in value:
        print(f"⚠️  {key}: {value} (needs configuration)")
    else:
        # Hide sensitive values
        if "TOKEN" in key or "SECRET" in key:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {key}: {masked_value}")
        else:
            print(f"✅ {key}: {value}")

# Try importing MCP
print("\n📦 Checking MCP installation...")
try:
    from mcp.server.fastmcp import FastMCP
    print("✅ MCP installed and importable")
except ImportError as e:
    print(f"❌ MCP import error: {e}")
    sys.exit(1)

# Try importing Google Auth
print("\n🔐 Checking Google Auth libraries...")
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    print("✅ Google Auth libraries installed")
except ImportError as e:
    print(f"❌ Google Auth import error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("📝 Setup Summary:")
print("="*50)

if all(v != "NOT_SET" and v != "" and "your_" not in v and "/path/to/" not in v for v in env_vars.values()):
    print("✅ All environment variables are configured!")
    print("\n🚀 Ready to run: make run")
else:
    print("⚠️  Some environment variables need configuration")
    print("\n📝 Next steps:")
    print("   1. Edit .env file with your actual credentials")
    print("   2. Make sure GOOGLE_ADS_CREDENTIALS_PATH points to valid file")
    print("   3. Run 'make run' to start the server")

print("\n💡 For testing without real credentials:")
print("   - The server will start but tools will fail with auth errors")
print("   - This is expected behavior for demo/development")
