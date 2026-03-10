from fastapi import APIRouter, UploadFile, File
from app.services.invoice_processor import process_pdf

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    """Upload un ou plusieurs fichiers PDF et les traite."""
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
            results.append({
                "status": "error",
                "pdf_filename": file.filename,
                "message": str(e),
            })

    return {"results": results}
