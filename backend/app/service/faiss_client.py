# app/service/faiss_client.py
import httpx
from google import genai
from typing import List, Dict, Any
import asyncio 

# K8s 내부 DNS 이름.
FAISS_SERVICE_URL = "http://faiss-db-service:8001" 
async def search_faiss_api(profile_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
    # ... httpx logic ...
    pass

def generate_embedding(client: genai.Client, profile_text: str) -> List[float]:
    """
    Gemini Embedding API를 호출하여 프로파일 텍스트를 벡터로 변환합니다.
    """
    if client is None:
        raise Exception("Gemini client not initialized for embedding.")

    # 동기식 API 호출
    response = client.models.embed_content(
        model='text-embedding-004', 
        content=profile_text
    )
    
    return response['embedding']