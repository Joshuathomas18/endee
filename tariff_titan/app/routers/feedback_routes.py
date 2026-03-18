from fastapi import APIRouter
from models.schemas import FeedbackCorrection
from config import settings
import json
import os

router = APIRouter(prefix="/feedback", tags=["Human Feedback"])

@router.post("/correct")
async def collect_feedback(feedback: FeedbackCorrection):
    feedback_dict = feedback.model_dump()
    
    # Load existing logs or create new
    if os.path.exists(settings.FEEDBACK_LOG_PATH):
        try:
            with open(settings.FEEDBACK_LOG_PATH, 'r') as f:
                logs = json.load(f)
        except:
            logs = []
    else:
        logs = []
        
    logs.append(feedback_dict)
    
    with open(settings.FEEDBACK_LOG_PATH, 'w') as f:
        json.dump(logs, f, indent=4)
        
    return {"status": "success", "message": "Feedback recorded. This will be embedded natively into Endee later."}
