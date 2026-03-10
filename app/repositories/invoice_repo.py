from tinydb import Query
from app.database import factures_table
from app.models import Facture, FactureCreate, FactureUpdate, now_iso


def get_all(client_id: str | None = None, vehicule_id: str | None = None) -> list[dict]:
    q = Query()
    conditions = []
    if client_id:
        conditions.append(q.client_id == client_id)
    if vehicule_id:
        conditions.append(q.vehicule_id == vehicule_id)

    if conditions:
        query = conditions[0]
        for c in conditions[1:]:
            query = query & c
        return factures_table.search(query)
    return factures_table.all()


def get_by_id(facture_id: str) -> dict | None:
    q = Query()
    results = factures_table.search(q.id == facture_id)
    return results[0] if results else None


def search_by_numero(numero_facture: str) -> dict | None:
    """Recherche par numéro de facture."""
    q = Query()
    results = factures_table.search(q.numero_facture == numero_facture)
    return results[0] if results else None


def create(data: FactureCreate) -> dict:
    facture = Facture(**data.model_dump())
    doc = facture.model_dump()
    factures_table.insert(doc)
    return doc


def update(facture_id: str, data: FactureUpdate) -> dict | None:
    q = Query()
    existing = get_by_id(facture_id)
    if not existing:
        return None
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updates["updated_at"] = now_iso()
    factures_table.update(updates, q.id == facture_id)
    return get_by_id(facture_id)


def delete(facture_id: str) -> bool:
    q = Query()
    removed = factures_table.remove(q.id == facture_id)
    return len(removed) > 0


def get_stats(client_id: str | None = None) -> dict:
    """Calcule les stats : total CA HT, TVA, nb factures."""
    factures = get_all(client_id=client_id)
    total_ht = sum(f.get("total_ht", 0) for f in factures)
    total_tva = sum(f.get("montant_tva", 0) for f in factures)
    total_ttc = sum(f.get("total_ttc", 0) for f in factures)
    return {
        "nb_factures": len(factures),
        "total_ht": round(total_ht, 2),
        "total_tva": round(total_tva, 2),
        "total_ttc": round(total_ttc, 2),
    }
