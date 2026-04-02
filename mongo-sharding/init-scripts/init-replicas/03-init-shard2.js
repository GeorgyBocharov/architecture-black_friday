print("\n2. Initializing shard2 replica set...");
db = connect("shard2:27019");
rs.initiate({
  _id: "shard2",
  members: [{ _id: 0, host: "shard2:27019" }]
});
print("Shard2 initialized");
