#!/bin/bash
set -e

echo "Starting Autogram services..."

# Start FastAPI in background
echo "Starting FastAPI on port 8000..."
uvicorn api.index:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to be ready
echo "Waiting for FastAPI to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "FastAPI is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "FastAPI failed to start"
        exit 1
    fi
    sleep 1
done

# Start Next.js
echo "Starting Next.js on port 3000..."
npm start

# If Next.js exits, kill FastAPI too
kill $FASTAPI_PID
