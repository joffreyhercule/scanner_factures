import logging
from fastapi import APIRouter, UploadFile, File
from app.services.invoice_processor import process_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    """Upload un ou plusieurs fichiers PDF et les traite."""
    logger.info("Upload reçu : %d fichier(s) - %s",
                len(files), ", ".join(f.filename or "?" for f in files))
    results = []
    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            results.append({
                "status": "error",
                "pdf_filename": file.filename or "unknown",
                "message": "Le fichier n'est pas un PDF",
            })
            continue

        try:
            pdf_bytes = await file.read()
            result = process_pdf(pdf_bytes, file.filename)
            results.append(result)
        except Exception as e:
            logger.error("Erreur traitement %s : %s", file.filename, e, exc_info=True)
            results.append({
                "status": "error",
                "pdf_filename": file.filename,
                "message": str(e),
            })

    return {"results": results}
