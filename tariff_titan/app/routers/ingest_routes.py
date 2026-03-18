from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from services.endee_rag_service import ingest_document
import os
import shutil

router = APIRouter(prefix="/ingest", tags=["Data Ingestion"])

@router.post("/pdf")
async def ingest_pdf(namespace: str = Form(...), file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported for ingestion.")
    
    # Save temp file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        result = ingest_document(temp_path, namespace)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
