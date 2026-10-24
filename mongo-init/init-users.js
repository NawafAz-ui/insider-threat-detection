// Runs once, on first start of an EMPTY MongoDB data folder (docker-compose.secure.yml).
// Write authorization from the proposal: only the engine account writes models, baselines, thresholds and results.
const dbName = "insider_threat";
const d = db.getSiblingDB(dbName);
d.createRole({
  role: "itdApi",
  privileges: [
    { resource: { db: dbName, collection: "results" }, actions: ["find"] },
    { resource: { db: dbName, collection: "runs" }, actions: ["find"] },
    { resource: { db: dbName, collection: "user_baselines" }, actions: ["find"] },
    { resource: { db: dbName, collection: "analyst_accounts" }, actions: ["find"] },
    { resource: { db: dbName, collection: "access_log" }, actions: ["find", "insert"] },   // the API's only write
  ],
  roles: [],
});
d.createUser({ user: "itd_engine", pwd: process.env.ITD_ENGINE_PASSWORD, roles: [{ role: "readWrite", db: dbName }] });
d.createUser({ user: "itd_api", pwd: process.env.ITD_API_PASSWORD, roles: ["itdApi"] });
