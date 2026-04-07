#!/bin/bash

docker compose exec -T redis-node1 redis-cli --cluster check redis-node1:6379

