#!/usr/bin/env python3
"""Simple test to verify Langfuse SDK connection and send a test trace."""

import os
import sys
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Get credentials
PUBLIC_KEY = "pk-lf-5238afee-5095-4088-a765-aba0a4c9c2e0"
SECRET_KEY = "sk-lf-31191733-72d7-4d74-a94a-e3cfc2fb767b"
BASE_URL = "https://cloud.langfuse.com"

print("Testing Langfuse connection...")
print(f"Public Key: {PUBLIC_KEY[:20]}...")
print(f"Secret Key: {SECRET_KEY[:20]}...")
print(f"Base URL: {BASE_URL}")
print()

try:
    from langfuse import Langfuse
    print("[OK] Langfuse SDK imported successfully")
except ImportError as e:
    print(f"[FAIL] Failed to import Langfuse SDK: {e}")
    sys.exit(1)

try:
    # Initialize Langfuse client
    client = Langfuse(
        public_key=PUBLIC_KEY,
        secret_key=SECRET_KEY,
        baseUrl=BASE_URL,
        environment="development",
        release="test",
        sample_rate=1.0,
        flushInterval=1.0,
    )
    print("[OK] Langfuse client initialized")
except Exception as e:
    print(f"[FAIL] Failed to initialize Langfuse client: {e}")
    sys.exit(1)

try:
    # Create a test trace with nested spans
    print("\nCreating test trace...")

    trace = client.trace(
        name="test_langfuse_connection",
        input={"test": "hello"},
        metadata={"source": "test_script", "timestamp": datetime.utcnow().isoformat()},
    )
    print(f"[OK] Trace created: {trace.id}")

    # Create a nested span
    span = client.span(
        name="test_span",
        trace_id=trace.id,
        input={"message": "This is a test span"},
        output={"result": "success"},
    )
    print(f"[OK] Span created: {span.id}")

    # Update trace with completion
    trace.update(
        output={"message": "Test trace completed successfully"},
        metadata={"completed": True},
    )
    print("[OK] Trace updated with output")

except Exception as e:
    print(f"[FAIL] Failed to create trace: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    # Flush traces to Langfuse
    print("\nFlushing traces to Langfuse...")
    client.flush(timeout_seconds=10)
    print("[OK] Traces flushed successfully")
except Exception as e:
    print(f"[FAIL] Failed to flush traces: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("SUCCESS! Test trace sent to Langfuse")
print("="*60)
print("\nNext steps:")
print("1. Go to https://cloud.langfuse.com")
print("2. Open your project dashboard")
print("3. Look for a trace named 'test_langfuse_connection'")
print("4. You should see it within 5-10 seconds")
print("\nIf you see the trace in Langfuse, the integration is working!")
print("If not, check:")
print("  - API keys are correct")
print("  - Project exists in Langfuse cloud")
print("  - Network connectivity to Langfuse (https://cloud.langfuse.com)")
