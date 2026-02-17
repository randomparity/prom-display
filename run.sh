#!/usr/bin/env bash
set -euo pipefail
podman rm -f prom-display 2>/dev/null || true
podman run -d --name prom-display --network host localhost/prom-display:latest
echo "Dashboard: http://localhost:9090/consoles/inference.html"
