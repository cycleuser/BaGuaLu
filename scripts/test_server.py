#!/usr/bin/env python3
"""Test server startup."""

import subprocess
import time
import requests
import sys


def test_server():
    """Test that the server can start and respond."""
    print("Starting server...")

    # Start server in background
    proc = subprocess.Popen(
        [sys.executable, "-m", "bagualu", "server", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(3)

    try:
        # Test root endpoint
        response = requests.get("http://localhost:8001/", timeout=5)

        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        return False
    finally:
        # Stop server
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
