# app/service/faiss_client.py 
import httpx
from google import genai
from google.genai import types
from typing import List, Dict, Any
import asyncio # asyncio.to_thread 사용
import time
import os

#FAISS_SERVICE_URL = "http://faiss-db-service:8001" 
FAISS_SERVICE_URL = os.getenv("FAISS_SERVICE_URL", "http://faiss-service:8000")   
async def search_faiss_api(profile_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
    """
    FAISS DB Pod의 /search 엔드포인트에 벡터 검색을 요청하고 응답을 받습니다.
    """
    
    # FAISS Pod가 실제로 /search 엔드포인트를 노출해야 작동.
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{FAISS_SERVICE_URL}/search",
                json={
                    "query_vector": profile_vector,
                    "k": k
                }
            )
            
            response.raise_for_status() 

            # FAISS Pod에서 반환한 JSON (메타데이터가 포함된 후보군 리스트)을 반환
            return response.json()

    except httpx.RequestError as e:
        # 연결 실패, 타임아웃 등 네트워크 오류 처리
        print(f"FATAL ERROR: Failed to connect to FAISS DB Service: {e}")
        raise e 
    except Exception as e:
        print(f"FATAL ERROR: FAISS response processing failed: {e}")
        raise e

MAX_RETRIES = 3
INITIAL_DELAY = 2

def generate_embedding_sync(client: genai.Client, profile_text: str) -> List[float]:
    """
    Gemini Embedding API를 호출하여 프로파일 텍스트를 벡터로 변환.
    """
    if client is None:
        raise Exception("Gemini client not initialized for embedding.")

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.embed_content(
                model="text-embedding-004",
                contents=[types.Content(
                    parts=[types.Part(text=profile_text)]
                )]
            ) 
            return response.embeddings[0].values
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_DELAY * (attempt + 1)
                print(f"WARNING: Gemini embedding generation failed (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay}s. Error: {e}")
                time.sleep(delay)
            else:
                print(f"FATAL ERROR: Gemini embedding generation failed after {MAX_RETRIES} attempts. Last Error: {e}")
                raise e

    raise Exception("Failed to generate embedding after retries.")

async def generate_embedding(client: genai.Client, profile_text: str) -> List[float]:
    return await asyncio.to_thread(generate_embedding_sync, client, profile_text)