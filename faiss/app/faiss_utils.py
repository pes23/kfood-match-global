# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np
import faiss
import json
import os
import logging

# 1. 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("faiss-service")

app = FastAPI(title="FAISS DB Vector Search API", version="1.0")

# 2. 환경 변수 설정
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024")) 

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/app/data/kfood_faiss.index")
METADATA_PATH = os.getenv("METADATA_PATH", "/app/data/kfood_metadata.json")

# 전역 변수
FAISS_INDEX: Optional[faiss.Index] = None
METADATA_MAP: Dict[int, Dict[str, Any]] = {}

class VectorSearchRequest(BaseModel):
    query_vector: List[float]
    k: int = 5

class CandidateItem(BaseModel):
    faiss_index: int
    id: int
    name_ko: str
    name_en: str
    category: str
    spicy_level: int
    image_url: str
    ingredients: List[str]  # 문자열 배열 ["쌀", "설탕"]
    description: str
    
    reason: Optional[str] = "" 

def create_mock_index(d: int, nb: int = 100):
    """실제 파일 로드 실패 시 사용할 Mock 데이터 생성 (새 스펙 반영)"""
    global FAISS_INDEX, METADATA_MAP
    
    logger.info(f"Creating MOCK Index with dim={d}, count={nb} (Schema Updated)")
    
    xb = np.random.random((nb, d)).astype('float32')
    FAISS_INDEX = faiss.IndexFlatL2(d)
    FAISS_INDEX.add(xb)
    
    METADATA_MAP.clear()
    for i in range(FAISS_INDEX.ntotal):
        METADATA_MAP[i] = {
            "faiss_index": i,
            "id": 1000 + i,
            "name_ko": f"모의 음식_{i}",
            "name_en": f"Mock Food {i}",
            "category": "Mock Category",
            "spicy_level": i % 5,
            "image_url": "https://via.placeholder.com/300?text=Mock+Food",
            "ingredients": ["Mock Ingredient 1", "Mock Ingredient 2"],
            "description": "This is a mock description because the actual data file was not loaded.",
            "reason": ""
        }
    logger.info("MOCK FAISS Index and Metadata generated successfully.")

def load_faiss_data():
    global FAISS_INDEX, METADATA_MAP

    try:
        if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(METADATA_PATH):
            raise FileNotFoundError("Index or Metadata file not found.")

        logger.info(f"Loading FAISS index from {FAISS_INDEX_PATH}...")
        FAISS_INDEX = faiss.read_index(FAISS_INDEX_PATH)
        
        logger.info(f"Loading Metadata from {METADATA_PATH}...")
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            raw_metadata = json.load(f)
            
            # FAISS 검색 결과(Index ID) -> JSON의 faiss_index
            METADATA_MAP = {item['faiss_index']: item for item in raw_metadata}
        
        logger.info(f"Successfully loaded actual FAISS data. Total vectors: {FAISS_INDEX.ntotal}")
        
        # 차원 검증
        if FAISS_INDEX.d != EMBEDDING_DIM:
            logger.warning(f"Dimension mismatch! Index: {FAISS_INDEX.d}, Config: {EMBEDDING_DIM}")

    except Exception as e:
        logger.warning(f"Failed to load actual FAISS data: {e}")
        logger.warning("Switching to MOCK mode for testing.")
        create_mock_index(d=EMBEDDING_DIM)

@app.on_event("startup")
async def startup_event():
    load_faiss_data()

@app.get("/health")
def health_check():
    if FAISS_INDEX is None:
        raise HTTPException(status_code=503, detail="Not ready")
    return {"status": "ok", "mode": "mock" if "Mock" in METADATA_MAP.get(0, {}).get('name_en', '') else "real"}

@app.post("/search", response_model=List[CandidateItem])
async def search_vectors(request: VectorSearchRequest):
    if FAISS_INDEX is None:
        raise HTTPException(status_code=503, detail="FAISS Index is not ready.")

    try:
        # 입력 차원 검증 (1024 차원인지 확인)
        input_dim = len(request.query_vector)
        if input_dim != FAISS_INDEX.d:
             raise ValueError(f"Dimension mismatch: Input {input_dim} vs Index {FAISS_INDEX.d}")

        query_vector = np.array(request.query_vector).astype('float32').reshape(1, -1)
        k = min(request.k, FAISS_INDEX.ntotal)
        
        if k == 0:
            return []

        D, I = FAISS_INDEX.search(query_vector, k)
        
        results = []
        for index_id in I[0]:
            if index_id != -1 and int(index_id) in METADATA_MAP:
                item_data = METADATA_MAP[int(index_id)]
                # Pydantic 모델이 자동으로 검증 및 변환 수행
                results.append(CandidateItem(**item_data))
                
        return results

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))