#!/bin/bash

# Online Judge Development Environment Stop Script
# This script stops all services using docker compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.dev.yml"

echo "========================================"
echo "Stopping Online Judge Services"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running."
    exit 1
fi

# Stop services
echo "Stopping services..."
docker compose -f "$COMPOSE_FILE" down

echo ""
echo "========================================"
echo "Services Stopped Successfully!"
echo "========================================"
echo ""
echo "To start services again:"
echo "  ./scripts/start.sh"
echo ""
