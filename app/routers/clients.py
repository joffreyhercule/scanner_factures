from fastapi import APIRouter, HTTPException
from app.models import ClientCreate, ClientUpdate
from app.repositories import client_repo

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("")
def list_clients():
    return client_repo.get_all()


@router.get("/{client_id}")
def get_client(client_id: str):
    client = client_repo.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client


@router.post("", status_code=201)
def create_client(data: ClientCreate):
    return client_repo.create(data)


@router.put("/{client_id}")
def update_client(client_id: str, data: ClientUpdate):
    client = client_repo.update(client_id, data)
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client


@router.delete("/{client_id}")
def delete_client(client_id: str):
    if not client_repo.delete(client_id):
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return {"ok": True}
