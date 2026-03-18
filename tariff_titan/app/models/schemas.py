from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# Mistral Extracted Item representation
class ExtractedItem(BaseModel):
    item_description: str = Field(description="Detailed description of the product or item")
    quantity: Optional[str] = Field(default="Not Provided", description="Quantity of the item")
    unit_price: Optional[str] = Field(default="Not Provided", description="Unit price or value of the item")
    factory_hs_code: Optional[str] = Field(default="Not Provided", description="HS code provided by the factory if any")
    context_notes: Optional[str] = Field(default="Not Provided", description="Any other context or notes for the item")

class ExtractionData(BaseModel):
    status: str = "success"
    filename: str
    total_items_found: int
    data: List[ExtractedItem]


# RAG Search representation
class RAGQuery(BaseModel):
    query: str
    top_k: int = Field(default=3, description="Number of top results to return")

class RAGResultItem(BaseModel):
    content: str
    score: float = Field(description="Mathematical similarity score")
    metadata: Dict[str, Any]

class RAGSearchResponse(BaseModel):
    results: List[RAGResultItem]

# Gemini Final Output representation
class ClassificationResult(BaseModel):
    final_hsn: str = Field(description="The determined HSN code")
    import_duty_rate: str = Field(description="The applicable import duty rate at importation")
    compliance_documents: List[str] = Field(description="List of required compliance documents for this item based on customs rules")
    official_desc: str = Field(description="Official description of the item")
    import_policy: str = Field(description="E.g., FREE, RESTRICTED, PROHIBITED")
    confidence_level: str = Field(description="e.g., High, Medium, Low")
    legal_rationale: str = Field(description="Chain-of-thought reasoning based on the Endee retrieved context")

class RAGContext(BaseModel):
    hsn_codes_context: List[RAGResultItem] = Field(default_factory=list, description="Relevant HSN codes context returned from Endee")
    customs_laws_context: List[RAGResultItem] = Field(default_factory=list, description="Relevant customs laws context returned from Endee")

class ClassificationRequest(BaseModel):
    item_description: str
    extracted_data: Optional[ExtractedItem] = None

class FullOrchestrationResponse(BaseModel):
    classifications: List[ClassificationResult]

# Feedback Schema
class FeedbackCorrection(BaseModel):
    original_text: str
    ai_hsn: str
    user_corrected_hsn: str
