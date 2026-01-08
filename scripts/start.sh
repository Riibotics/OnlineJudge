#!/bin/bash

# Online Judge Development Environment Start Script
# This script starts all services using docker compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.dev.yml"

echo "========================================"
echo "Starting Online Judge Services"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Pull latest images if needed
echo "Checking for image updates..."
docker compose -f "$COMPOSE_FILE" pull --quiet

# Build and start services
echo "Building and starting services..."
docker compose -f "$COMPOSE_FILE" up -d --build

echo ""
echo "Waiting for services to be ready..."
sleep 5

# Show status
echo ""
echo "========================================"
echo "Service Status:"
echo "========================================"
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "========================================"
echo "Services Started Successfully!"
echo "========================================"
echo ""
echo "Access points:"
echo "  - Frontend (User):  http://localhost:8080"
echo "  - Frontend (Admin): http://localhost:8080/admin"
echo "  - Backend API:      http://localhost:8000/api"
echo "  - PostgreSQL:       localhost:5432"
echo "  - Redis:            localhost:6379"
echo ""
echo "Default admin credentials:"
echo "  - Username: root"
echo "  - Password: rootroot"
echo ""
echo "To view logs:"
echo "  docker logs oj-backend-dev"
echo "  docker logs oj-frontend-dev"
echo ""
echo "To stop services:"
echo "  ./scripts/stop.sh"
echo ""
