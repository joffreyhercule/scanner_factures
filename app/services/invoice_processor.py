import logging
from pathlib import Path
from app.services.ai_parser import parse_invoice_pdf
from app.repositories import client_repo, vehicle_repo, invoice_repo
from app.models import ClientCreate, VehiculeCreate, FactureCreate
from app.config import IMAGES_DIR

logger = logging.getLogger(__name__)


def save_images(facture_id: str, images: list[bytes]) -> list[str]:
    """Sauvegarde les images PNG des pages et retourne les noms de fichiers."""
    filenames = []
    for i, img_bytes in enumerate(images):
        filename = f"{facture_id}_page{i + 1}.png"
        (IMAGES_DIR / filename).write_bytes(img_bytes)
        filenames.append(filename)
    return filenames


def process_pdf(pdf_bytes: bytes, pdf_filename: str) -> dict:
    """Traite un PDF de facture : extraction IA + upsert en base."""

    logger.info("=== Traitement PDF : %s (%d octets) ===", pdf_filename, len(pdf_bytes))

    # 1. Extraction via Ollama/Qwen 3.5
    data, images = parse_invoice_pdf(pdf_bytes)

    client_data = data.get("client", {})
    vehicule_data = data.get("vehicule", {})
    facture_data = data.get("facture", {})

    # 2. Upsert client
    existing_client = None
    if client_data.get("nom"):
        existing_client = client_repo.search_by_nom(client_data["nom"])

    if existing_client:
        client_id = existing_client["id"]
        logger.info("Client existant trouvé : %s (id=%s)", existing_client["nom"], client_id)
    else:
        client = client_repo.create(ClientCreate(
            nom=client_data.get("nom", "Inconnu"),
            adresse=client_data.get("adresse"),
            telephone=client_data.get("telephone"),
            email=client_data.get("email"),
        ))
        client_id = client["id"]
        logger.info("Nouveau client créé : %s (id=%s)", client_data.get("nom"), client_id)

    # 3. Upsert véhicule
    existing_vehicule = None
    immat = vehicule_data.get("immatriculation")
    if immat:
        existing_vehicule = vehicle_repo.search_by_immatriculation(immat)

    if existing_vehicule:
        vehicule_id = existing_vehicule["id"]
        logger.info("Véhicule existant trouvé : %s (id=%s)", existing_vehicule["immatriculation"], vehicule_id)
    else:
        vehicule = vehicle_repo.create(VehiculeCreate(
            client_id=client_id,
            marque=vehicule_data.get("marque", "Inconnu"),
            modele=vehicule_data.get("modele", "Inconnu"),
            immatriculation=immat or "Inconnu",
            vin=vehicule_data.get("vin"),
            annee=vehicule_data.get("annee"),
            kilometrage=vehicule_data.get("kilometrage"),
        ))
        vehicule_id = vehicule["id"]
        logger.info("Nouveau véhicule créé : %s (id=%s)", immat, vehicule_id)

    # 4. Upsert facture
    numero = facture_data.get("numero_facture", "")
    existing_facture = None
    if numero:
        existing_facture = invoice_repo.search_by_numero(numero)

    lignes = facture_data.get("lignes", [])

    if existing_facture:
        facture_id = existing_facture["id"]
        result_action = "updated"
        logger.info("Facture existante trouvée : %s (id=%s)", numero, facture_id)
    else:
        facture = invoice_repo.create(FactureCreate(
            numero_facture=numero or f"SANS-NUM-{pdf_filename}",
            client_id=client_id,
            vehicule_id=vehicule_id,
            date_facture=facture_data.get("date_facture", ""),
            lignes=lignes,
            total_ht=facture_data.get("total_ht", 0),
            tva_taux=facture_data.get("tva_taux", 20.0),
            montant_tva=facture_data.get("montant_tva", 0),
            total_ttc=facture_data.get("total_ttc", 0),
            pdf_filename=pdf_filename,
        ))
        facture_id = facture["id"]
        result_action = "created"
        logger.info("Nouvelle facture créée : %s, HT=%.2f, TTC=%.2f (id=%s)",
                     numero, facture_data.get("total_ht", 0), facture_data.get("total_ttc", 0), facture_id)

    # 5. Sauvegarder les images des pages
    save_images(facture_id, images)
    logger.info("=== Traitement terminé : %s -> %s ===", pdf_filename, result_action)

    return {
        "status": "success",
        "action": result_action,
        "facture_id": facture_id,
        "client_id": client_id,
        "vehicule_id": vehicule_id,
        "pdf_filename": pdf_filename,
    }
