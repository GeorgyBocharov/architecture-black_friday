print("\n2. Initializing shard1 replica set...");
db = connect("shard1:27018");
rs.initiate({
  _id: "shard1",
  members: [{ _id: 0, host: "shard1:27018" }]
});
print("Shard1 initialized");