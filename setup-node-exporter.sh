#!/usr/bin/env bash
set -euo pipefail

VERSION="1.8.2"
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64)  ARCH="amd64" ;;
  aarch64) ARCH="arm64" ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

TARBALL="node_exporter-${VERSION}.linux-${ARCH}.tar.gz"
URL="https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/${TARBALL}"
TMPDIR="$(mktemp -d)"

echo "Downloading node_exporter v${VERSION} for ${ARCH}..."
curl -fsSL "$URL" -o "${TMPDIR}/${TARBALL}"
tar -xzf "${TMPDIR}/${TARBALL}" -C "$TMPDIR"

echo "Installing to /usr/local/bin/node_exporter..."
sudo install -m 0755 "${TMPDIR}/node_exporter-${VERSION}.linux-${ARCH}/node_exporter" /usr/local/bin/node_exporter
rm -rf "$TMPDIR"

echo "Creating systemd service..."
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<'EOF'
[Unit]
Description=Prometheus Node Exporter
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/node_exporter
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter

echo "node_exporter is running. Verify with: curl -s localhost:9100/metrics | head"
