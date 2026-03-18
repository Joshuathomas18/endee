from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pandas as pd
from io import BytesIO

from models.schemas import ClassificationRequest, ClassificationResult, FullOrchestrationResponse, ExtractionData
from services.endee_rag_service import retrieve_context
from services.gemini_service import classify_customs_item
from services.mistral_service import extract_items_from_document

router = APIRouter(prefix="", tags=["Classification and Orchestration"])

@router.post("/classify/text", response_model=ClassificationResult)
async def classify_text(request: ClassificationRequest):
    # RAG Lookups
    hsn_context = retrieve_context(request.item_description, "hsn_codes", top_k=5)
    law_context = retrieve_context(request.item_description, "customs_laws", top_k=3)
    
    # Gemini Classification
    result = await classify_customs_item(request.model_dump(), hsn_context, law_context)
    return result


@router.post("/classify/bulk-excel")
async def classify_bulk_excel(file: UploadFile = File(...), target_column: str = "item_description"):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
         raise HTTPException(status_code=400, detail="Only Excel or CSV files are supported")
         
    content = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(BytesIO(content))
    else:
        df = pd.read_excel(BytesIO(content))
        
    if target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{target_column}' not found in the file")

    results = []
    for index, row in df.iterrows():
        description = str(row[target_column])
        
        # RAG Lookups
        hsn_context = retrieve_context(description, "hsn_codes", top_k=5)
        law_context = retrieve_context(description, "customs_laws", top_k=3)
        
        # Gemini Classification
        item_dict = {"item_description": description}
        result = await classify_customs_item(item_dict, hsn_context, law_context)
        
        row_dict = row.to_dict()
        row_dict['AI_HSN_Code'] = result.final_hsn
        row_dict['AI_Import_Policy'] = result.import_policy
        row_dict['AI_Rationale'] = result.legal_rationale
        row_dict['AI_Confidence'] = result.confidence_level
        row_dict['AI_Official_Desc'] = result.official_desc
        results.append(row_dict)
        
    result_df = pd.DataFrame(results)
    
    # Returning dict for simplicity here, in a real app would return StreamingResponse of Excel bytes
    return result_df.to_dict(orient="records")


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/orchestrate/full-pipeline", response_model=FullOrchestrationResponse)
async def full_pipeline(file: UploadFile = File(...)):
    # 1. Validation Constraints
    valid_types = ["application/pdf", "image/jpeg", "image/png", "image/webp"]
    if file.content_type not in valid_types:
        raise HTTPException(status_code=400, detail="File type not supported. Please upload PDF, JPEG, PNG, or WEBP.")
        
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the 10MB limit.")

    # 2. Extract Items with Mistral
    extraction_result: ExtractionData = await extract_items_from_document(file)
    
    classifications = []
    
    # 2. Iterate and Classify
    for item in extraction_result.data:
        description = item.item_description
        if item.quantity and item.quantity != "Not Provided":
            description += f" (Qty: {item.quantity})"
            
        hsn_context = retrieve_context(description, "hsn_codes", top_k=5)
        law_context = retrieve_context(description, "customs_laws", top_k=3)
        
        cls_result = await classify_customs_item(item.model_dump(), hsn_context, law_context)
        classifications.append(cls_result)
        
    return FullOrchestrationResponse(classifications=classifications)
