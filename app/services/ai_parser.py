import json
import logging
import base64
import time
import io
import fitz  # PyMuPDF
import ollama
from app.config import OLLAMA_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es un assistant spécialisé dans l'extraction de données de factures de garage automobile (réparation de véhicules).

À partir du document PDF fourni, extrais les informations suivantes et retourne-les en JSON valide.

Structure attendue :
{
  "client": {
    "nom": "Nom du client (personne ou entreprise)",
    "adresse": "Adresse complète ou null",
    "telephone": "Numéro de téléphone ou null",
    "email": "Email ou null"
  },
  "vehicule": {
    "marque": "Marque du véhicule (ex: Renault)",
    "modele": "Modèle (ex: Clio)",
    "immatriculation": "Plaque d'immatriculation (ex: AB-123-CD)",
    "vin": "Numéro VIN ou null",
    "annee": 2020,
    "kilometrage": 85000
  },
  "facture": {
    "numero_facture": "Numéro de la facture",
    "date_facture": "Date au format YYYY-MM-DD",
    "lignes": [
      {
        "description": "Description de la prestation ou pièce",
        "quantite": 1.0,
        "prix_unitaire_ht": 50.0,
        "montant_ht": 50.0,
        "type": "main_oeuvre"
      }
    ],
    "total_ht": 100.0,
    "tva_taux": 20.0,
    "montant_tva": 20.0,
    "total_ttc": 120.0
  }
}

Règles :
- Les montants sont des nombres décimaux (float), pas des chaînes.
- Le type de ligne est "main_oeuvre" pour la main d'œuvre, "piece" pour les pièces détachées, "autre" sinon.
- Si un champ n'est pas trouvé dans le document, utilise null.
- Les dates doivent être au format YYYY-MM-DD.
- Réponds UNIQUEMENT avec du JSON valide, sans markdown, sans explication."""


def pdf_to_images(pdf_bytes: bytes) -> list[bytes]:
    """Convertit chaque page du PDF en image PNG."""
    logger.info("Conversion PDF -> images (%d octets)", len(pdf_bytes))
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        logger.info("  Page %d : %d x %d px, %d octets PNG", i + 1, pix.width, pix.height, len(img_bytes))
        images.append(img_bytes)
    doc.close()
    logger.info("Conversion terminée : %d page(s)", len(images))
    return images


def parse_invoice_pdf(pdf_bytes: bytes) -> tuple[dict, list[bytes]]:
    """Convertit le PDF en images puis envoie à Ollama/Qwen 3.5 pour extraction.
    Retourne (données extraites, liste des images PNG)."""
    images = pdf_to_images(pdf_bytes)
    images_b64 = [base64.b64encode(img).decode("utf-8") for img in images]

    logger.info("Appel Ollama - modèle: %s, %d image(s), taille totale b64: %d",
                OLLAMA_MODEL, len(images_b64), sum(len(b) for b in images_b64))

    start = time.time()
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": SYSTEM_PROMPT + "\n\nAnalyse cette facture et extrais les données.",
                    "images": images_b64,
                }
            ],
            format="json",
        )
    except Exception as e:
        logger.error("Erreur appel Ollama après %.1fs : %s", time.time() - start, e)
        raise

    elapsed = time.time() - start
    content = response.message.content

    logger.info("Réponse Ollama en %.1fs (%d caractères)", elapsed, len(content))
    logger.debug("Réponse brute Ollama :\n%s", content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Erreur parsing JSON de la réponse Ollama : %s", e)
        logger.error("Contenu reçu :\n%s", content)
        raise

    logger.info("Données extraites - client: %s, véhicule: %s, facture n°%s",
                data.get("client", {}).get("nom", "?"),
                data.get("vehicule", {}).get("immatriculation", "?"),
                data.get("facture", {}).get("numero_facture", "?"))

    return data, images
