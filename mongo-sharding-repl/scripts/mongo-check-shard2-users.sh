#!/bin/bash

###
# Инициализируем бд
###

docker compose exec -T shard2-node1 mongosh --port 27019 --quiet<<EOF
use mobile_world
db.users.countDocuments()
EOF

