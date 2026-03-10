from fastapi import APIRouter, HTTPException, Query
from app.models import FactureCreate, FactureUpdate
from app.repositories import invoice_repo
from app.config import IMAGES_DIR

router = APIRouter(prefix="/api/factures", tags=["factures"])


@router.get("/stats")
def get_stats(client_id: str | None = Query(default=None)):
    return invoice_repo.get_stats(client_id=client_id)


@router.get("")
def list_factures(
    client_id: str | None = Query(default=None),
    vehicule_id: str | None = Query(default=None),
):
    return invoice_repo.get_all(client_id=client_id, vehicule_id=vehicule_id)


@router.get("/{facture_id}/images")
def get_facture_images(facture_id: str):
    """Liste les URLs des images de pages de cette facture."""
    facture = invoice_repo.get_by_id(facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    images = sorted(IMAGES_DIR.glob(f"{facture_id}_page*.png"))
    return [f"/images/{img.name}" for img in images]


@router.get("/{facture_id}")
def get_facture(facture_id: str):
    facture = invoice_repo.get_by_id(facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


@router.post("", status_code=201)
def create_facture(data: FactureCreate):
    return invoice_repo.create(data)


@router.put("/{facture_id}")
def update_facture(facture_id: str, data: FactureUpdate):
    facture = invoice_repo.update(facture_id, data)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


@router.delete("/{facture_id}")
def delete_facture(facture_id: str):
    if not invoice_repo.delete(facture_id):
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return {"ok": True}
