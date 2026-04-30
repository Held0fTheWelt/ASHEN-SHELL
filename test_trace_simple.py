#!/usr/bin/env python3
"""Simple Langfuse trace test - works with LANGFUSE_* environment variables."""

import os
import sys
import time
from dotenv import load_dotenv

# Load from .env or environment
load_dotenv()

print("=" * 70)
print("Simple Langfuse Trace Test")
print("=" * 70)

# Check for credentials in environment
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

print(f"\n[CONFIG]")
print(f"  LANGFUSE_BASE_URL: {base_url}")
print(f"  LANGFUSE_PUBLIC_KEY: {'YES' if public_key else 'MISSING'}")
print(f"  LANGFUSE_SECRET_KEY: {'YES' if secret_key else 'MISSING'}")

if not public_key or not secret_key:
    print("\n[ERROR] Langfuse credentials not found in environment")
    print("  Set these environment variables:")
    print("    export LANGFUSE_PUBLIC_KEY=pk_...")
    print("    export LANGFUSE_SECRET_KEY=sk_...")
    print("    export LANGFUSE_BASE_URL=https://cloud.langfuse.com  (optional)")
    sys.exit(1)

print("\n[✓] Credentials found")

# Initialize Langfuse with FIXED parameter name
print("\n[INIT] Initializing Langfuse SDK with base_url parameter (v4.x)...")
try:
    from langfuse import Langfuse, observe

    client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        base_url=base_url,  # ✅ THIS IS THE FIX - using base_url, not host or baseUrl
    )
    print("[✓] Langfuse client initialized successfully")
except Exception as e:
    print(f"[ERROR] Initialization failed: {e}")
    sys.exit(1)

# Send test traces
print("\n[TRACE] Sending test traces...")

@observe()
def sample_function():
    """A simple function to trace."""
    time.sleep(0.2)
    return "Hello from World of Shadows!"

try:
    # Trace 1: Using decorator
    print("  1. Calling sample_function() [traced with @observe()]...")
    result = sample_function()
    print(f"     → Result: {result}")

    # Trace 2: Using direct observation
    print("  2. Creating direct observation span...")
    span = client.start_observation(
        as_type="span",
        name="world_of_shadows.test_trace",
        metadata={
            "test": "direct_span",
            "timestamp": time.time(),
            "description": "Test trace to verify Langfuse tracing works",
        }
    )
    time.sleep(0.1)
    span.end()
    print("     → Observation closed")

    # Flush
    print("\n[FLUSH] Sending all traces to Langfuse...")
    client.flush()
    print("[✓] Flush completed")

except Exception as e:
    print(f"[ERROR] Trace failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Wait for transmission
print("\n[WAIT] Allowing 2 seconds for traces to transmit...")
time.sleep(2)

print("\n" + "=" * 70)
print("✅ SUCCESS - Traces sent to Langfuse!")
print("=" * 70)
print(f"\nOpen your Langfuse dashboard to verify:")
print(f"  {base_url}")
print("\nLook for these traces:")
print("  • sample_function (from @observe decorator)")
print("  • world_of_shadows.test_trace (direct observation)\n")
