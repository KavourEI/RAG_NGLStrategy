#!/usr/bin/env python3
"""
Script to verify Streamlit secrets configuration
Run this locally to ensure your secrets are set up correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

print("=" * 60)
print("Streamlit Secrets Configuration Verification")
print("=" * 60)

# Required secrets
required_secrets = [
    ('LLAMA_CLOUD_API_KEY', 'LlamaCloud API Key'),
    ('LLAMA_ORG_ID', 'LlamaCloud Organization ID'),
    ('OLLAMA_API_KEY', 'Ollama Cloud API Key'),
]

all_set = True

for secret_key, description in required_secrets:
    value = os.getenv(secret_key)
    if value:
        # Show first and last 4 chars for security
        display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
        print(f"✅ {description}: {display_value}")
    else:
        print(f"❌ {description}: NOT SET")
        all_set = False

print("=" * 60)

if all_set:
    print("✅ All required secrets are configured!")
    print("\nTo use these secrets in Streamlit Cloud:")
    print("1. Go to your Streamlit Cloud app settings")
    print("2. Navigate to 'Secrets' section")
    print("3. Copy the values from your .env file or local environment")
    print("4. Paste them in Streamlit Secrets (TOML format):")
    print()
    print("Example:")
    for secret_key, _ in required_secrets:
        value = os.getenv(secret_key)
        if value:
            print(f'{secret_key} = "{value}"')
else:
    print("❌ Some secrets are missing!")
    print("\nPlease set the following environment variables:")
    for secret_key, description in required_secrets:
        print(f"  - {secret_key}: {description}")
    sys.exit(1)
