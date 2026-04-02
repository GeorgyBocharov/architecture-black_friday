#!/bin/bash
set -e

echo "=== Initializing Config Server ==="
mongosh --host configSrv --port 27017 /scripts/01-init-config.js

echo "=== Initializing Shard1 ==="
mongosh --host shard1 --port 27018 /scripts/02-init-shard1.js

echo "=== Initializing Shard2 ==="
mongosh --host shard2 --port 27019 /scripts/03-init-shard2.js

echo "=== Success ==="