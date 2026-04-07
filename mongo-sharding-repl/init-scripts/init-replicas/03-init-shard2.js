print("\n2. Initializing shard2 replica set...");
rs.initiate({
  _id: "shard2",
  members: [
    { _id: 0, host: "shard2-node1:27019" },
    { _id: 1, host: "shard2-node2:27019" },
    { _id: 2, host: "shard2-node3:27019" }
  ]
});
print("Shard2 initialized");
