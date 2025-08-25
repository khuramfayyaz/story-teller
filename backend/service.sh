#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source venv/bin/activate
# Bind to all interfaces so the internet can reach it
uvicorn app:app --host 0.0.0.0 --port 8000


