from fastapi import APIRouter, HTTPException, Query
from app.models import VehiculeCreate, VehiculeUpdate
from app.repositories import vehicle_repo

router = APIRouter(prefix="/api/vehicules", tags=["vehicules"])


@router.get("")
def list_vehicules(client_id: str | None = Query(default=None)):
    return vehicle_repo.get_all(client_id=client_id)


@router.get("/{vehicule_id}")
def get_vehicule(vehicule_id: str):
    vehicule = vehicle_repo.get_by_id(vehicule_id)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return vehicule


@router.post("", status_code=201)
def create_vehicule(data: VehiculeCreate):
    return vehicle_repo.create(data)


@router.put("/{vehicule_id}")
def update_vehicule(vehicule_id: str, data: VehiculeUpdate):
    vehicule = vehicle_repo.update(vehicule_id, data)
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return vehicule


@router.delete("/{vehicule_id}")
def delete_vehicule(vehicule_id: str):
    if not vehicle_repo.delete(vehicule_id):
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return {"ok": True}
