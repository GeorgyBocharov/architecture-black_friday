#!/bin/bash

###
# Инициализируем бд
###

docker compose exec -T shard1-node1 mongosh --port 27018 --quiet<<EOF
use mobile_world
db.users.countDocuments()
EOF

