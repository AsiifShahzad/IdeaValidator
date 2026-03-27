#!/bin/bash
set -e

# Ensure PORT is set (default to 8000 if not provided)
PORT=${PORT:-8000}

echo "🚀 Starting Idea Validator API on port $PORT..."

# Run uvicorn with explicit port
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port $PORT \
  --workers 1
