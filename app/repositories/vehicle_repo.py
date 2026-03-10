from tinydb import Query
from app.database import vehicules_table
from app.models import Vehicule, VehiculeCreate, VehiculeUpdate, new_id, now_iso


def normalize_immat(immat: str) -> str:
    return immat.upper().replace(" ", "").replace("-", "")


def get_all(client_id: str | None = None) -> list[dict]:
    if client_id:
        q = Query()
        return vehicules_table.search(q.client_id == client_id)
    return vehicules_table.all()


def get_by_id(vehicule_id: str) -> dict | None:
    q = Query()
    results = vehicules_table.search(q.id == vehicule_id)
    return results[0] if results else None


def search_by_immatriculation(immatriculation: str) -> dict | None:
    """Recherche par immatriculation normalisée."""
    normalized = normalize_immat(immatriculation)
    q = Query()
    results = vehicules_table.search(
        q.immatriculation.test(lambda v: normalize_immat(v) == normalized)
    )
    return results[0] if results else None


def create(data: VehiculeCreate) -> dict:
    vehicule = Vehicule(**data.model_dump())
    doc = vehicule.model_dump()
    vehicules_table.insert(doc)
    return doc


def update(vehicule_id: str, data: VehiculeUpdate) -> dict | None:
    q = Query()
    existing = get_by_id(vehicule_id)
    if not existing:
        return None
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updates["updated_at"] = now_iso()
    vehicules_table.update(updates, q.id == vehicule_id)
    return get_by_id(vehicule_id)


def delete(vehicule_id: str) -> bool:
    q = Query()
    removed = vehicules_table.remove(q.id == vehicule_id)
    return len(removed) > 0
