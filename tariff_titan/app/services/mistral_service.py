import os
import base64
from fastapi import UploadFile, HTTPException
from mistralai import Mistral
from config import settings
from models.schemas import ExtractionData

client = Mistral(api_key=settings.MISTRAL_API_KEY)

async def extract_items_from_document(file: UploadFile) -> ExtractionData:
    # Read the file and convert to base64
    try:
        content = await file.read()
        base64_image = base64.b64encode(content).decode('utf-8')
    except Exception:
        raise HTTPException(status_code=400, detail="File is unreadable or encrypted.")
        
    mime_type = file.content_type
    
    # We construct the multimodal message
    messages = [
        {
            "role": "system",
            "content": "You are a specialized OCR extraction engine for customs documents. Your job is to extract physical product line items from invoices or packing lists. If the page is blank or contains no products (e.g., Terms & Conditions), return an empty list for 'data' and 0 for 'total_items_found'. Do NOT include markdown blocks."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract the line items from this document image. Return a structured JSON response matching the provided schema exactly."
                },
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{base64_image}"
                }
            ]
        }
    ]
    
    # Use Pixtral model and parse the response with Pydantic
    try:
        chat_response = client.chat.parse(
            model="pixtral-large-latest",
            messages=messages,
            response_format=ExtractionData,
            temperature=0.1
        )
        parsed_data = chat_response.choices[0].message.parsed
        
        # Inject metadata that Mistral shouldn't guess
        parsed_data.filename = file.filename
        parsed_data.total_items_found = len(parsed_data.data)
        return parsed_data
        
    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        # Identify if it was an API timeout/availability issue or a parsing error
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            raise HTTPException(status_code=502, detail="OCR Engine currently unavailable. Please try again in 60 seconds.")
        else:
            raise HTTPException(status_code=500, detail="Failed to parse document structure.")
