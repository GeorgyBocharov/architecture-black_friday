const DB_NAME = process.env.DB_NAME || "mobile_world";
const COLLECTION_NAME = process.env.COLLECTION_NAME || "users";

print("4. MongoDB Cluster Configuration");
print(`Database: ${DB_NAME}`);
print(`Collection: ${COLLECTION_NAME}`);

print("Adding shards to cluster...");
db = connect("mongos_router:27020");
sh.addShard("shard1/shard1:27018");
sh.addShard("shard2/shard2:27019");
sh.enableSharding(DB_NAME);
sh.shardCollection(`${DB_NAME}.${COLLECTION_NAME}`, {"_id": "hashed"});

print("\nAll done! Cluster initialization complete.");