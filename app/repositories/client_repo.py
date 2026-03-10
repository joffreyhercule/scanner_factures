from tinydb import Query
from app.database import clients_table
from app.models import Client, ClientCreate, ClientUpdate, new_id, now_iso


def get_all() -> list[dict]:
    return clients_table.all()


def get_by_id(client_id: str) -> dict | None:
    q = Query()
    results = clients_table.search(q.id == client_id)
    return results[0] if results else None


def search_by_nom(nom: str) -> dict | None:
    """Recherche par nom normalisé (insensible à la casse, sans espaces superflus)."""
    normalized = nom.strip().lower()
    q = Query()
    results = clients_table.search(
        q.nom.test(lambda v: v.strip().lower() == normalized)
    )
    return results[0] if results else None


def create(data: ClientCreate) -> dict:
    client = Client(**data.model_dump())
    doc = client.model_dump()
    clients_table.insert(doc)
    return doc


def update(client_id: str, data: ClientUpdate) -> dict | None:
    q = Query()
    existing = get_by_id(client_id)
    if not existing:
        return None
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updates["updated_at"] = now_iso()
    clients_table.update(updates, q.id == client_id)
    return get_by_id(client_id)


def delete(client_id: str) -> bool:
    q = Query()
    removed = clients_table.remove(q.id == client_id)
    return len(removed) > 0
