from fastapi import APIRouter, UploadFile, File, HTTPException
from services.mistral_service import extract_items_from_document
from models.schemas import ExtractionData

router = APIRouter(prefix="/extract", tags=["Document Extraction"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/document", response_model=ExtractionData)
async def extract_document(file: UploadFile = File(...)):
    # 1. Content Type Check
    valid_types = ["application/pdf", "image/jpeg", "image/png", "image/webp"]
    if file.content_type not in valid_types:
        raise HTTPException(status_code=400, detail="File type not supported. Please upload PDF, JPEG, PNG, or WEBP.")
    
    # 2. File Size Check (FastAPI reads the spool)
    # Note: UploadFile in FastAPI defaults to SpooledTemporaryFile
    # To check size, we can seek to end, get pos, then seek back
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the 10MB limit.")
        
    # 3. Process the extraction
    extraction_result = await extract_items_from_document(file)
    return extraction_result
