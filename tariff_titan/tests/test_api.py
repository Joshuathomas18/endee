import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to sys.path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_health_check_boots_server():
    """
    This test verifies that the server can start, all routers are imported 
    correctly, and the lifespan context manager executes without crashing.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "message": "Customs AI engine is running and ready to process invoices."
    }

def test_orchestrator_rejects_invalid_file():
    """
    Verifies that the orchestrator endpoint is mounted and correctly 
    enforces the filetype limitations defined in the PRD.
    """
    response = client.post(
        "/api/v1/orchestrate/full-pipeline",
        files={"file": ("test.txt", b"dummy content", "text/plain")}
    )
    # The endpoint should return a 400 Bad Request if it's not an allowed image/pdf
    assert response.status_code == 400
    assert "File type not supported" in response.json()["detail"] or "invalid" in response.json()["detail"].lower()
    
def test_extract_endpoint_size_limit():
    """
    Verifies that the /extract/document endpoint enforces the 10MB limit.
    """
    # Create an 11MB dummy payload
    large_payload = b"0" * (11 * 1024 * 1024)
    response = client.post(
        "/api/v1/extract/document",
        files={"file": ("large_image.jpg", large_payload, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "10MB" in response.json()["detail"]
