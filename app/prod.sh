#!/bin/bash

echo "HumanizeTrace (production)"
echo "Using only docker-compose.yml (ignoring override file)"
echo ""
echo "Services run in Docker network with production build"
echo "   - Frontend exposed at http://localhost:5173"
echo "   - Backend stay internal"
echo "   - Optimized build with pre-compiled assets"
echo "   - API calls use internal service names"
echo "Building and starting production containers..."
echo ""

# Run docker-compose without override file
docker compose up --build -d

# echo "Production environment stopped" 
echo "Production environment started (detached mode)"