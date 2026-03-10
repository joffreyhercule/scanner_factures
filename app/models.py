from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4
from datetime import datetime


def new_id() -> str:
    return str(uuid4())


def now_iso() -> str:
    return datetime.now().isoformat()


# --- Client ---

class ClientBase(BaseModel):
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None


class Client(ClientBase):
    id: str = Field(default_factory=new_id)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


# --- Véhicule ---

class VehiculeBase(BaseModel):
    client_id: str
    marque: str
    modele: str
    immatriculation: str
    vin: Optional[str] = None
    annee: Optional[int] = None
    kilometrage: Optional[int] = None


class VehiculeCreate(VehiculeBase):
    pass


class VehiculeUpdate(BaseModel):
    client_id: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    immatriculation: Optional[str] = None
    vin: Optional[str] = None
    annee: Optional[int] = None
    kilometrage: Optional[int] = None


class Vehicule(VehiculeBase):
    id: str = Field(default_factory=new_id)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


# --- Facture ---

class LigneFacture(BaseModel):
    description: str
    quantite: float
    prix_unitaire_ht: float
    montant_ht: float
    type: str = "autre"  # "main_oeuvre", "piece", "autre"


class FactureBase(BaseModel):
    numero_facture: str
    client_id: str
    vehicule_id: str
    date_facture: str
    lignes: list[LigneFacture] = []
    total_ht: float
    tva_taux: float = 20.0
    montant_tva: float
    total_ttc: float
    pdf_filename: str


class FactureCreate(FactureBase):
    pass


class FactureUpdate(BaseModel):
    numero_facture: Optional[str] = None
    client_id: Optional[str] = None
    vehicule_id: Optional[str] = None
    date_facture: Optional[str] = None
    lignes: Optional[list[LigneFacture]] = None
    total_ht: Optional[float] = None
    tva_taux: Optional[float] = None
    montant_tva: Optional[float] = None
    total_ttc: Optional[float] = None
    pdf_filename: Optional[str] = None


class Facture(FactureBase):
    id: str = Field(default_factory=new_id)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
