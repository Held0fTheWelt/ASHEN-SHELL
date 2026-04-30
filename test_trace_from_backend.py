#!/usr/bin/env python3
"""Get Langfuse credentials from backend and send a test trace."""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

print("=" * 70)
print("Langfuse Tracing Verification (via Backend)")
print("=" * 70)

# Get backend credentials
backend_url = os.getenv("BACKEND_INTERNAL_URL", "http://localhost:8000")
internal_token = os.getenv("INTERNAL_RUNTIME_CONFIG_TOKEN", "")

print(f"\n[CONFIG]")
print(f"  Backend URL: {backend_url}")
print(f"  Internal Token: {internal_token[:20] if internal_token else 'MISSING'}...")

if not internal_token:
    print("\n[WARNING] INTERNAL_RUNTIME_CONFIG_TOKEN not set in environment")
    print("  Using default backend at http://localhost:8000")
    backend_url = "http://localhost:8000"
    internal_token = ""

# Try to fetch credentials from backend
print(f"\n[FETCHING] Credentials from backend endpoint...")
try:
    endpoint = f"{backend_url}/api/v1/internal/observability/langfuse-credentials"
    headers = {"X-Internal-Config-Token": internal_token} if internal_token else {}

    response = requests.get(endpoint, headers=headers, timeout=5)

    if response.status_code == 200:
        data = response.json().get("data", {})
        public_key = data.get("public_key", "").strip()
        secret_key = data.get("secret_key", "").strip()
        base_url = data.get("base_url", "https://cloud.langfuse.com").strip()

        print(f"[✓] Retrieved from backend")
        print(f"    Public Key: {public_key[:20]}...")
        print(f"    Secret Key: {secret_key[:20]}...")
        print(f"    Base URL: {base_url}")

        if not public_key or not secret_key:
            print("\n[ERROR] Backend returned empty credentials")
            sys.exit(1)
    else:
        print(f"[ERROR] Backend returned {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        sys.exit(1)

except requests.ConnectionError:
    print(f"[ERROR] Cannot connect to backend at {backend_url}")
    print("  Make sure backend is running (python docker-up.py)")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Failed to fetch credentials: {e}")
    sys.exit(1)

# Now send a test trace with the retrieved credentials
print("\n[INITIALIZING] Langfuse SDK with backend credentials...")
try:
    from langfuse import Langfuse, observe

    client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        base_url=base_url,
    )
    print("[✓] Langfuse client initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize Langfuse: {e}")
    sys.exit(1)

print("\n[SENDING] Test traces to Langfuse...")

@observe()
def test_backend_trace():
    """Test trace from backend credentials."""
    time.sleep(0.3)
    return {"status": "success"}

try:
    print("  • Executing test_backend_trace()...")
    result = test_backend_trace()
    print(f"    → {result}")

    print("  • Creating direct span...")
    span = client.start_observation(
        as_type="span",
        name="world_of_shadows.langfuse_test",
        metadata={
            "test_type": "backend_credential_test",
            "timestamp": time.time(),
            "source": "test_trace_from_backend.py",
        }
    )
    time.sleep(0.2)
    span.end()
    print("    → Done")

except Exception as e:
    print(f"[ERROR] Failed to send trace: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[FLUSHING] Sending traces to Langfuse...")
try:
    client.flush()
    print("[✓] Flush completed")
except Exception as e:
    print(f"[WARNING] Flush failed: {e}")

# Wait for transmission
print("\n[WAITING] 3 seconds for traces to transmit...")
time.sleep(3)

print("\n" + "=" * 70)
print("SUCCESS - Test traces sent to Langfuse!")
print("=" * 70)
print(f"\nVerify in Langfuse dashboard ({base_url}):")
print("  • Look for trace: 'test_backend_trace'")
print("  • Look for trace: 'world_of_shadows.langfuse_test'")
print("  • Check metadata contains 'test_type' and 'source'\n")
