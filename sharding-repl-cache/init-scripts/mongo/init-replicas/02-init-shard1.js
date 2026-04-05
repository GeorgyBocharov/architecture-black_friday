print("\n2. Initializing shard1 replica set...");
rs.initiate({
  _id: "shard1",
  members: [
    { _id: 0, host: "shard1-node1:27018" },
    { _id: 1, host: "shard1-node2:27018" },
    { _id: 2, host: "shard1-node3:27018" }
  ]
});
print("Shard1 initialized");