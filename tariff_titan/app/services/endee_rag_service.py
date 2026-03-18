import httpx
import logging
from config import settings
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

embeddings_model = None

def get_embeddings():
    global embeddings_model
    if embeddings_model is None:
        embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return embeddings_model

def ingest_document(pdf_path: str, namespace: str):
    logger.info(f"Ingesting {pdf_path} into namespace: {namespace}")
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        
        embedder = get_embeddings()
        
        payloads = []
        for i, chunk in enumerate(chunks):
            embedding = embedder.embed_query(chunk.page_content)
            payloads.append({
                "id": str(i),
                "vector": embedding,
                "payload": {"content": chunk.page_content, "metadata": chunk.metadata}
            })
            
        with httpx.Client() as client:
            # Endee HTTP API structure
            url = f"{settings.ENDEE_HOST}:{settings.ENDEE_PORT}/collections/{namespace}/points"
            response = client.post(url, json={"points": payloads}, timeout=30.0)
            response.raise_for_status()
            logger.info(f"Successfully ingested {len(payloads)} chunks to Endee namespace: {namespace}")
            return {"status": "success", "chunks_ingested": len(payloads)}
    except Exception as e:
        logger.error(f"Failed to ingest document to Endee: {e}")
        raise

def retrieve_context(query: str, namespace: str, top_k: int = 3) -> List[Dict[str, Any]]:
    logger.info(f"Retrieving context from Endee for query in {namespace}")
    try:
        embedder = get_embeddings()
        query_vector = embedder.embed_query(query)
        
        with httpx.Client() as client:
            url = f"{settings.ENDEE_HOST}:{settings.ENDEE_PORT}/collections/{namespace}/search"
            response = client.post(url, json={"vector": query_vector, "limit": top_k}, timeout=10.0)
            
            if response.status_code == 200:
                results = response.json().get("result", [])
                return [
                    {
                        "content": res.get("payload", {}).get("content", ""),
                        "score": res.get("score", 0.0),
                        "metadata": res.get("payload", {}).get("metadata", {})
                    }
                    for res in results
                ]
            else:
                logger.warning(f"Failed Endee search: {response.text}")
                return []
    except Exception as e:
        logger.error(f"Error querying Endee: {e}")
        return [{"content": f"Mock {namespace} Data due to connection failure", "score": 0.9, "metadata": {}}]
