from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from app.config import DB_PATH


def get_db() -> TinyDB:
    """Crée une instance TinyDB. Avec CachingMiddleware pour la robustesse."""
    return TinyDB(
        str(DB_PATH),
        indent=2,
        ensure_ascii=False,
        storage=CachingMiddleware(JSONStorage),
    )


db = get_db()

clients_table = db.table("clients")
vehicules_table = db.table("vehicules")
factures_table = db.table("factures")
