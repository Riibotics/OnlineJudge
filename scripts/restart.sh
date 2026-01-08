#!/bin/bash

# Online Judge Development Environment Restart Script
# This script restarts all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "Restarting Online Judge Services"
echo "========================================"
echo ""

"$SCRIPT_DIR/stop.sh"
echo ""
echo "Waiting 3 seconds before restart..."
sleep 3
echo ""
"$SCRIPT_DIR/start.sh"
