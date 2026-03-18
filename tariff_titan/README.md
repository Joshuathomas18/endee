# Tariff Titan: Automated Customs Compliance Engine

Tariff Titan is a production-ready, automated customs compliance pipeline representing a paradigm shift in how global trade documentation is evaluated and processed.

## Problem Statement

Navigating international trade barriers and customs laws is an intensely challenging operational hurdle. It relies on thousands of dense regulatory documents, dynamic tariff rates, and massive directories mapping unstructured descriptions to formal HSN codes. 
Traditional compliance relies on slow, error-prone human operators evaluating invoices and interpreting laws. This results in costly penalties, operational delays, and inefficient supply chains. A highly accurate, AI-driven automation layer is strictly required.

## The Solution: Endee-Powered Architecture

Tariff Titan functions as an automated agenting system that mimics human operational workflows: 

1. **Extraction (Vision & Parsing):** Unstructured documents (invoices, packing lists up to 10MB) are ingested and structured into discrete line items using Vision OCR Models (Mistral "Pixtral").
2. **Context Retrieval (Vector Store Memory):** The true "brain" of the agent relies on an extremely fast and reliable Open-Source Vector Database: **Endee**. We replaced standard local FAISS arrays with an Endee instance deployed over an HTTP API, storing vectors inside distinct `namespaces` (`hsn_codes` and `customs_laws`).
3. **Reasoning Orchestration (Gemini):** A primary LLM orchestrator (Gemini 2.5 Flash) ingests the original extracted item, the mathematically correlated legal context fetched synchronously from Endee, and outputs a highly deterministic JSON (`ClassificationResult`) predicting the HSN Code, Duty Rate, and required compliance framework.

## Why Endee?

Endee operates as the RAG database layer, transforming high-dimensional search queries into instantaneous structural context. Endee provides the system with:
- **Scalability**: Unlike local/in-memory FAISS arrays, Endee runs as an independent infrastructure layer handling thousands of simultaneous semantic queries across vast embedded regulations architectures.
- **Namespacing & Filtering**: By distinctly segregating Indian Customs Law PDFs and HSN Code directories into isolated payload structures, search noise is strictly localized. Endee queries only return pure legal context or pure category alignment context.

## Setup Instructions

### 1. Endee WSL Deployment (Windows Users)
You must install WSL (Windows Subsystem for Linux) because Endee runs over a C++ Linux layer.
1. Open PowerShell as Administrator and run:
   ```powershell
   wsl --install
   ```
   *(Restart your PC if prompted)*
2. Open the new "Ubuntu" terminal app from your Windows Start Menu.
3. Navigate to the project root and build Endee:
   ```bash
   cd /mnt/c/Users/User/Desktop/Hackathon/endee
   chmod +x ./install.sh ./run.sh
   ./install.sh --release --avx2
   ./run.sh
   ```
   *(Wait until the server says it is listening on port 8888)*

### 2. Python Backend Setup
1. Define `.env` at `tariff_titan/.env` with your `MISTRAL_API_KEY` and `GEMINI_API_KEY`.
2. Open a standard Windows Terminal (PowerShell/CMD).
3. Navigate to the backend app and run:
   ```powershell
   cd C:\Users\User\Desktop\Hackathon\endee\tariff_titan\app
   pip install -r ../requirements.txt
   python -m uvicorn main:app --reload --port 8000
   ```
