import json
import google.generativeai as genai
from config import settings
from models.schemas import ClassificationResult

# --- 1. CONFIGURATION ---
genai.configure(api_key=settings.GEMINI_API_KEY)

# Use Flash for speed and cost-efficiency in bulk processing
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 3. THE REASONING ENGINE ---
async def classify_customs_item(ocr_item: dict, hsn_context: list, law_context: list) -> ClassificationResult:
    """
    Takes the isolated item from Mistral and the context from Endee, 
    and forces Gemini to make a final legal classification.
    """
    print(f"🧠 Gemini is classifying: {ocr_item.get('item_description', 'Unknown Item')}...")

    # Construct the context payload
    prompt = f"""
    You are the Chief Customs Officer for a major freight forwarding SaaS.
    Your job is to classify the following imported good based strictly on the provided RAG context.

    --- INPUT DATA ---
    User's Commercial Invoice Item: {json.dumps(ocr_item, indent=2)}

    --- HSN DATABASE MATCHES (RAG) ---
    {json.dumps(hsn_context, indent=2)}

    --- CUSTOMS LAW MATCHES (RAG) ---
    {json.dumps(law_context, indent=2)}

    --- INSTRUCTIONS ---
    1. Analyze the User's Item Description.
    2. Find the most mathematically and logically accurate match in the HSN Database Matches.
    3. Check the Customs Law Matches to see if the item is prohibited, restricted, or free.
    4. Provide your final classification, including applicable import duty rate and required compliance documents.
    5. Provide a brief, professional legal rationale.
    6. If the HSN matches are completely irrelevant to the item, set confidence_level to "Low" and pick the closest generic chapter.
    """

    try:
        # We enforce the Pydantic schema so Gemini physically cannot return bad JSON
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=ClassificationResult,
                temperature=0.1 # Very low temperature for highly deterministic legal answers
            )
        )
        
        # Parse the JSON string back into a Python dictionary
        final_decision = json.loads(response.text)
        print(f"   ✅ Gemini Decision: {final_decision['final_hsn']} ({final_decision['confidence_level']} Confidence)")
        
        return ClassificationResult(**final_decision)

    except Exception as e:
        print(f"   ❌ Gemini Classification Failed: {e}")
        # Return a safe fallback so the master loop doesn't crash
        return ClassificationResult(
            final_hsn="Error",
            import_duty_rate="Error",
            compliance_documents=[],
            official_desc="Classification Failed",
            import_policy="Unknown",
            confidence_level="Failed",
            legal_rationale=str(e)
        )
