const DB_NAME = process.env.DB_NAME || "mobile_world";
const COLLECTION_NAME = process.env.COLLECTION_NAME || "users";

try {
    print("4. MongoDB Cluster Configuration");
    print(`Database: ${DB_NAME}`);
    print(`Collection: ${COLLECTION_NAME}`);

    print("Adding shards to cluster...");
    sh.addShard("shard1/shard1-node1:27018");
    sh.addShard("shard2/shard2-node1:27019");

    sh.enableSharding(DB_NAME);
    sh.shardCollection(`${DB_NAME}.${COLLECTION_NAME}`, {"_id": "hashed"});

    print("\n=== Cluster Status ===");
    sh.status();

    print("\nAll done! Cluster initialization complete.");
} catch(e) {
    print(`Error: ${e.message}`);
    quit(1);
}
