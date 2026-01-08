#!/bin/bash

# Online Judge Development Environment Logs Script
# This script shows logs from all or specific services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.dev.yml"

cd "$PROJECT_ROOT"

# Check if service name is provided
if [ -z "$1" ]; then
    echo "Showing logs from all services (press Ctrl+C to exit)..."
    echo ""
    docker compose -f "$COMPOSE_FILE" logs -f
else
    SERVICE_NAME="$1"
    echo "Showing logs from $SERVICE_NAME (press Ctrl+C to exit)..."
    echo ""
    docker compose -f "$COMPOSE_FILE" logs -f "$SERVICE_NAME"
fi
