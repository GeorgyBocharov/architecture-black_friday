#!/bin/bash
set -e

echo 'Waiting for Redis nodes...'
sleep 10

echo 'Creating Redis cluster...'
# редис при включении кластера из 6 нод с параметром --replicas = 1 сам создат 3 мастера и 3 реплики 
redis-cli --cluster create \
    redis-node1:6379 \
    redis-node2:6379 \
    redis-node3:6379 \
    redis-node4:6379 \
    redis-node5:6379 \
    redis-node6:6379 \
    --cluster-replicas 1 \
    --cluster-yes

echo 'Redis cluster created!'

echo 'Cluster info:'
redis-cli --cluster check redis-node1:6379

echo 'Initialization complete!'