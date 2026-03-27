#!/usr/bin/env python
"""
Startup script for Render deployment
Ensures proper port binding and error handling
"""
import os
import subprocess
import sys

# Get port from environment or use default
port = os.getenv('PORT', '8000')

print(f"🚀 Starting Idea Validator API on port {port}...")

try:
    # Run uvicorn with explicit port binding
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'main:app',
        '--host', '0.0.0.0',
        '--port', str(port),
        '--workers', '1'
    ], check=True)
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    sys.exit(1)
