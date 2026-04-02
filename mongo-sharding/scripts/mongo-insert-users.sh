#!/bin/bash

###
# Инициализируем бд
###

docker compose exec -T mongos_router mongosh --port 27020 --quiet<<EOF
use mobile_world
for(var i = 0; i < 1000; i++) db.users.insertOne({age:i, name:"ly"+i})
EOF

