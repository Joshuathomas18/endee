from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import ocr_routes, ingest_routes, classify_routes, feedback_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Endee DB via HTTP
    print("Connecting to Endee Vector DB...")
    yield
    # Shutdown
    print("Shutting down Customs AI Backend...")

app = FastAPI(
    title="Customs AI Enterprise Orchestrator",
    description="High-speed compliance engine for automated customs clearance and HSN classification.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ocr_routes.router, prefix="/api/v1")
app.include_router(ingest_routes.router, prefix="/api/v1")
app.include_router(classify_routes.router, prefix="/api/v1")
app.include_router(feedback_routes.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "message": "Customs AI engine is running and ready to process invoices."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
