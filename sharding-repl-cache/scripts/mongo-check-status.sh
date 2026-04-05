#!/bin/bash

###
# Инициализируем бд
###

docker compose exec -T mongos_router1 mongosh --port 27020 <<EOF
use mobile_world
sh.status()
EOF

