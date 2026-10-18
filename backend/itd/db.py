"""MongoDB access (PyMongo + GridFS). MONGO_URI=mock uses mongomock for tests.
get_db("engine") and get_db("api") may use different MongoDB accounts (write authorization)."""
import gridfs
from . import config

_clients, _dbs, _fs = {}, {}, None


def _uri(role):
    return {"engine": config.MONGO_URI_ENGINE, "api": config.MONGO_URI_API}.get(role, config.MONGO_URI)


def get_db(role="engine"):
    global _fs
    if role not in _dbs:
        if config.MONGO_URI == "mock":
            import mongomock
            from mongomock.gridfs import enable_gridfs_integration
            enable_gridfs_integration()
            if "mock" not in _clients:
                _clients["mock"] = mongomock.MongoClient()
            client = _clients["mock"]
        else:
            from pymongo import MongoClient
            client = MongoClient(_uri(role), serverSelectionTimeoutMS=5000)
        _dbs[role] = client[config.DB_NAME]
    return _dbs[role]


def get_fs():
    """GridFS for the trained models. Engine only: the API account has no access to it."""
    global _fs
    if _fs is None:
        _fs = gridfs.GridFS(get_db("engine"))
    return _fs


def reset_for_tests():
    global _fs
    _clients.clear(); _dbs.clear(); _fs = None
