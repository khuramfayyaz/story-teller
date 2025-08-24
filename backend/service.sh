#!/usr/bin/env bash
# Navigate to backend folder
cd "$(dirname "$0")"

# Default port 8000 unless overridden
export PORT=${PORT:-8000}

# Start FastAPI backend with Uvicorn (1 worker, listening on all interfaces)
uvicorn app:app --host 0.0.0.0 --port "$PORT" --workers 1
