#!/bin/bash
set -e

echo "Waiting for replica sets to stabilize..."
sleep 10

echo "=== Configuring Cluster ==="
mongosh --host mongos_router1 --port 27020 /scripts/01-configure-cluster.js

echo "=== Initialization Complete ==="