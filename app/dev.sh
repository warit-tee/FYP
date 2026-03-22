#!/bin/bash

echo "HumanizeTrace (development)"
echo "Using docker-compose.dev.yml for hot reload"
echo ""
echo "Services run with bind mounts for live code updates"
echo "   - Frontend: http://localhost:5174"
echo "   - Backend:  http://localhost:8000"
echo "   - No image rebuild needed for normal code edits"
echo ""
echo "Building (if needed) and starting development containers..."
echo ""

docker compose -f docker-compose.dev.yml up --build -d

echo "Development environment started (detached mode)"
