import inspect
import hashlib
import json
import logging
import os
import sys
import asyncio
from typing import List, Optional

import motor.motor_asyncio
from bson import ObjectId
from fastapi import Body, FastAPI, HTTPException, status
from logmiddleware import RouterLoggingMiddleware, logging_config
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from pymongo import errors
from redis.cluster import RedisCluster, ClusterNode
from typing_extensions import Annotated

print("=" * 60, flush=True)
print("APP STARTING", flush=True)
print("=" * 60, flush=True)

# Configure JSON logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    RouterLoggingMiddleware,
    logger=logger,
)

DATABASE_URL = os.environ["MONGODB_URL"]
DATABASE_NAME = os.environ["MONGODB_DATABASE_NAME"]
REDIS_URL = os.getenv("REDIS_URL", None)

print(f"REDIS_URL={REDIS_URL}", flush=True)

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]

PyObjectId = Annotated[str, BeforeValidator(str)]

# Глобальный клиент Redis
redis_client = None


@app.on_event("startup")
async def startup():
    global redis_client
    if REDIS_URL:
        try:
            # Парсим URL для кластера
            parts = REDIS_URL.replace("redis://", "").split("@")
            password = parts[0].replace(":", "") if len(parts) > 1 else None
            hosts_part = parts[1] if len(parts) > 1 else parts[0]
            
            startup_nodes = []
            for host_port in hosts_part.split(","):
                host, port = host_port.split(":")
                startup_nodes.append(ClusterNode(host, int(port)))

            redis_client = RedisCluster(
                startup_nodes=startup_nodes,
                password=password,
                decode_responses=True
            )
            

            redis_client.ping()
            print("✓ Redis Cluster connected successfully", flush=True)
        except Exception as e:
            print(f"✗ Redis connection failed: {e}", flush=True)
            redis_client = None
    else:
        print("Redis not configured", flush=True)


def cache_result(ttl: int = 60):
    """Простой декоратор кэширования для Redis Cluster"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            global redis_client
            if not redis_client:
                # Если Redis недоступен, просто вызываем функцию
                return await func(*args, **kwargs)
            
            # Создаем уникальный ключ
            key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            cache_key = f"api:cache:{key_data}"
            
            try:
                # Пробуем получить из кэша
                cached = redis_client.get(cache_key)
                if cached:
                    print(f"✓ CACHE HIT: {cache_key}", flush=True)
                    return json.loads(cached)
                
                print(f"✗ CACHE MISS: {cache_key}", flush=True)
                result = await func(*args, **kwargs)
                
                # Сохраняем в кэш
                redis_client.setex(cache_key, ttl, json.dumps(result.dict(by_alias=True), default=str))
                return result
            except Exception as e:
                print(f"Cache error: {e}", flush=True)
                return await func(*args, **kwargs)
        
        wrapper.__signature__ = inspect.signature(func)
        return wrapper
    return decorator


class UserModel(BaseModel):
    """
    Container for a single user record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    age: int = Field(...)
    name: str = Field(...)


class UserCollection(BaseModel):
    """
    A container holding a list of `UserModel` instances.
    """

    users: List[UserModel]


@app.get("/")
async def root():
    collection_names = await db.list_collection_names()
    collections = {}
    for collection_name in collection_names:
        collection = db.get_collection(collection_name)
        collections[collection_name] = {
            "documents_count": await collection.count_documents({})
        }
    try:
        replica_status = await client.admin.command("replSetGetStatus")
        replica_status = json.dumps(replica_status, indent=2, default=str)
    except errors.OperationFailure:
        replica_status = "No Replicas"

    topology_description = client.topology_description
    read_preference = client.client_options.read_preference
    topology_type = topology_description.topology_type_name
    replicaset_name = topology_description.replica_set_name

    shards = None
    if topology_type == "Sharded":
        shards_list = await client.admin.command("listShards")
        shards = {}
        for shard in shards_list.get("shards", {}):
            shards[shard["_id"]] = shard["host"]

    cache_enabled = False
    if REDIS_URL:
        cache_enabled = True

    redis_status = await get_redis_cluster_status()

    return {
        "mongo_topology_type": topology_type,
        "mongo_replicaset_name": replicaset_name,
        "mongo_db": DATABASE_NAME,
        "read_preference": str(read_preference),
        "collections": collections,
        "shards": shards,
        "cache_enabled": cache_enabled,
        "redis": redis_status,
        "status": "OK",
    }


@app.get("/{collection_name}/count")
async def collection_count(collection_name: str):
    collection = db.get_collection(collection_name)
    items_count = await collection.count_documents({})
    return {"status": "OK", "mongo_db": DATABASE_NAME, "items_count": items_count}


@app.get(
    "/{collection_name}/users",
    response_description="List all users",
    response_model=UserCollection,
    response_model_by_alias=False,
)
@cache_result(ttl=60)  # ← используем наш декоратор
async def list_users(collection_name: str):
    """
    List all of the user data in the database.
    The response is unpaginated and limited to 1000 results.
    """
    print(f"=== Computing list_users for {collection_name} ===", flush=True)
    await asyncio.sleep(3)  # 3 секунды задержки для проверки кэша
    collection = db.get_collection(collection_name)
    users = await collection.find().to_list(1000)
    print(f"Found {len(users)} users", flush=True)
    return UserCollection(users=users)


@app.get(
    "/{collection_name}/users/{name}",
    response_description="Get a single user",
    response_model=UserModel,
    response_model_by_alias=False,
)
async def show_user(collection_name: str, name: str):
    """
    Get the record for a specific user, looked up by `name`.
    """

    collection = db.get_collection(collection_name)
    if (user := await collection.find_one({"name": name})) is not None:
        return user

    raise HTTPException(status_code=404, detail=f"User {name} not found")


@app.post(
    "/{collection_name}/users",
    response_description="Add new user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(collection_name: str, user: UserModel = Body(...)):
    """
    Insert a new user record.

    A unique `id` will be created and provided in the response.
    """
    collection = db.get_collection(collection_name)
    new_user = await collection.insert_one(
        user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await collection.find_one({"_id": new_user.inserted_id})
    return created_user

async def get_redis_cluster_status():
    """Получение статуса Redis кластера"""
    redis_status = {
        "enabled": False,
        "connected": False,
        "cluster_size": None,
        "nodes_count": None,
        "cluster_state": None,
        "masters": [],
    }
    
    if not REDIS_URL:
        redis_status["enabled"] = False
        return redis_status
    
    redis_status["enabled"] = True
    
    if not redis_client:
        redis_status["connected"] = False
        return redis_status
    
    try:
        # Проверяем соединение
        redis_client.ping()
        redis_status["connected"] = True
        
        # Получаем информацию о кластере
        cluster_info = redis_client.cluster_info()
        if cluster_info:
            redis_status["cluster_state"] = cluster_info.get("cluster_state")
            redis_status["cluster_size"] = int(cluster_info.get("cluster_size", 0))
            redis_status["nodes_count"] = int(cluster_info.get("cluster_known_nodes", 0))
        
        # Получаем список всех нод через CLUSTER NODES
        cluster_nodes_output = redis_client.execute_command('CLUSTER', 'NODES')
        
        masters = []
        replicas = []
        
        if cluster_nodes_output:
            for line in cluster_nodes_output.strip().split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) < 8:
                    continue
                
                node_id = parts[0]
                host_port = parts[1]
                flags = parts[2]
                master_id = parts[3]
                
                # Разбираем host и port
                if '@' in host_port:
                    host_port = host_port.split('@')[0]
                host, port = host_port.split(':')
                
                # Определяем роль
                is_master = 'master' in flags and 'slave' not in flags
                is_slave = 'slave' in flags or 'master' not in flags and master_id != '-'
                
                node_info = {
                    "id": node_id,
                    "host": host,
                    "port": int(port),
                    "flags": flags,
                }
                
                if is_master:
                    node_info["replicas_count"] = 0
                    masters.append(node_info)
                else:
                    # Это реплика
                    node_info["master_id"] = master_id if master_id != '-' else None
                    replicas.append(node_info)
        
        # Связываем реплики с мастерами
        for master in masters:
            master["replicas"] = [
                {
                    "host": r["host"],
                    "port": r["port"],
                    "id": r["id"]
                }
                for r in replicas if r.get("master_id") == master["id"]
            ]
            master["replicas_count"] = len(master["replicas"])
        
        redis_status["masters"] = masters
        
        # Добавляем краткую сводку
        redis_status["summary"] = {
            "masters_count": len(masters),
            "replicas_count": len(replicas),
            "total_nodes": len(masters) + len(replicas),
        }
        
    except Exception as e:
        redis_status["connected"] = False
        redis_status["error"] = str(e)
        
    return redis_status


print("=" * 60, flush=True)
print("APP MODULE LOADED", flush=True)
print("=" * 60, flush=True)