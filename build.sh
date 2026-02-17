#!/usr/bin/env bash
set -euo pipefail
podman build -t localhost/prom-display:latest .
