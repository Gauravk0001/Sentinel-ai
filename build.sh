#!/usr/bin/env bash
# SentinelAI build script for Render native Python runtime.
# Runs from the repository root (all repo files are included in the deploy).
# Installs backend Python dependencies and builds the React frontend
# into frontend/dist, which the backend serves as static files with SPA fallback.

set -e

echo "=== Building SentinelAI ==="

# 1. Install backend Python dependencies
echo "Installing backend Python dependencies..."
pip install --no-cache-dir -r backend/requirements.txt

# 2. Build the frontend
if [ -d "frontend" ]; then
  echo "Installing frontend dependencies..."
  cd frontend
  npm ci --no-audit --no-fund
  echo "Building frontend..."
  npm run build
  echo "Frontend build complete. Output: $(pwd)/dist"
  cd ..
else
  echo "WARNING: frontend directory not found. Skipping frontend build."
fi

echo "=== Build complete ==="
