#!/usr/bin/env python3
"""End-to-End Langfuse tracing test.

This test verifies that story turns are properly traced to Langfuse Cloud.
It creates a test session, executes a turn, and verifies the trace appears in Langfuse.
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Backend API URL
BACKEND_URL = "http://localhost:8000"

# Test credentials
TEST_USERNAME = "admin"
TEST_PASSWORD = "Admin123"

def log_step(step: str):
    """Log a test step with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] {step}")

def get_admin_token():
    """Get JWT token for admin user."""
    log_step("1. Logging in as admin...")
    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        timeout=10
    )
    if response.status_code != 200:
        print(f"[FAIL] Login failed: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    token = data.get("access_token")
    if token:
        print(f"[OK] Login successful")
    return token

def create_test_session(token: str):
    """Create a test player session."""
    log_step("2. Creating test player session...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BACKEND_URL}/api/v1/player/session",
        headers=headers,
        timeout=10
    )

    if response.status_code != 200:
        print(f"[FAIL] Session creation failed: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    session_id = data.get("session", {}).get("id")
    if session_id:
        print(f"[OK] Session created: {session_id}")
    return session_id

def execute_story_turn(token: str, session_id: str):
    """Execute a story turn and get the trace_id."""
    log_step("3. Executing story turn...")

    headers = {"Authorization": f"Bearer {token}"}
    player_input = f"Test input from Langfuse E2E test at {datetime.now().isoformat()}"

    response = requests.post(
        f"{BACKEND_URL}/api/v1/sessions/{session_id}/turns",
        json={"player_input": player_input},
        headers=headers,
        timeout=30
    )

    print(f"   Response status: {response.status_code}")
    data = response.json() if response.text else {}

    if response.status_code not in (200, 502):
        print(f"[FAIL] Turn execution failed: {response.status_code}")
        print(response.text)
        return None

    trace_id = data.get("trace_id")
    if trace_id:
        print(f"[OK] Story turn executed")
        print(f"  trace_id: {trace_id}")
    else:
        print(f"[WARN] No trace_id in response (status: {response.status_code})")

    return trace_id, data

def verify_langfuse_trace(trace_id: str):
    """Verify the trace exists in Langfuse Cloud."""
    if not trace_id:
        print("[FAIL] No trace_id to verify")
        return False

    log_step("4. Waiting for Langfuse Cloud to receive trace...")
    time.sleep(2)  # Give time for async flush

    log_step("5. Verifying trace in Langfuse Cloud...")

    try:
        from langfuse import Langfuse

        client = Langfuse(
            public_key="pk-lf-fc5a5d54-0590-43ca-9015-8ac71b97ada9",
            secret_key="sk-lf-6efeda4c-fb23-46b1-8f6d-da23f396dca7",
            base_url="https://cloud.langfuse.com"
        )

        # Try to retrieve the trace
        trace = client.get_trace(trace_id)

        if trace:
            print(f"[OK] Trace found in Langfuse Cloud!")
            print(f"  Trace ID: {trace.id}")
            print(f"  Trace Name: {trace.name}")
            return True
        else:
            print(f"[FAIL] Trace {trace_id} not found in Langfuse Cloud")
            return False

    except Exception as e:
        print(f"[FAIL] Error verifying trace: {e}")
        return False

def main():
    """Run the E2E test."""
    print("=" * 70)
    print("LANGFUSE E2E TRACING TEST")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started: {datetime.now().isoformat()}")

    # Step 1: Login
    token = get_admin_token()
    if not token:
        print("\n[FAIL] TEST FAILED: Could not get admin token")
        return False

    # Step 2: Create session
    session_id = create_test_session(token)
    if not session_id:
        print("\n[FAIL] TEST FAILED: Could not create test session")
        return False

    # Step 3: Execute turn
    result = execute_story_turn(token, session_id)
    if not result:
        print("\n[FAIL] TEST FAILED: Could not execute story turn")
        return False

    trace_id, response_data = result

    # Step 4-5: Verify trace in Langfuse
    success = verify_langfuse_trace(trace_id)

    # Summary
    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] TEST PASSED: Trace verified in Langfuse Cloud")
        print(f"   Session: {session_id}")
        print(f"   Trace ID: {trace_id}")
    else:
        print("[FAIL] TEST FAILED: Trace not found in Langfuse Cloud")
        print(f"   Session: {session_id}")
        print(f"   Trace ID: {trace_id}")
    print("=" * 70)

    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
