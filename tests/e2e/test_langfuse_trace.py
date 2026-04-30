#!/usr/bin/env python3
"""Simple test to verify Langfuse SDK connection and send a test trace."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Get credentials
PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
BASE_URL = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

print("Testing Langfuse connection...")
print(f"Public Key: {PUBLIC_KEY[:20]}...")
print(f"Secret Key: {SECRET_KEY[:20]}...")
print(f"Base URL: {BASE_URL}")
print()

if not PUBLIC_KEY or not SECRET_KEY:
    print("[FAIL] Missing credentials")
    sys.exit(1)

print("[OK] Starting Langfuse test")

# ✅ THIS is the correct import in v4.x
from langfuse import observe, Langfuse

# Initialize client (required)
langfuse = Langfuse(
    public_key=PUBLIC_KEY,
    secret_key=SECRET_KEY,
    base_url=BASE_URL,
)

# Decorated function = automatically traced
@observe()
def main_task():
    return nested_task()

@observe()
def nested_task():
    return {"result": "success"}

try:
    result = main_task()
    print("[OK] Function executed:", result)

    # Ensure everything is sent
    import time

    time.sleep(2)
    langfuse.flush()
    time.sleep(2)

    print("\nSUCCESS — check Langfuse dashboard")

except Exception as e:
    print(f"[FAIL] Error: {e}")
    sys.exit(1)
