# faiss-db/app/faiss_utils.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np
import faiss
import json
import os
from contextlib import suppress

# FastAPI 인스턴스 초기화
app = FastAPI(title="FAISS DB Vector Search API", version="1.0")

# K8s 환경 변수 설정
# PV/PVC 사용 시: /mnt/data/ (외부 마운트 경로)
# PV/PVC 미사용 시: /faiss/data/ (이미지 내장 경로), K8s Deployment YAML 파일에서 환경 변수와 볼륨 설정을 통해 두 가지 상황에 유연하게 대응
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/faiss/data/kfood_faiss.index")
METADATA_PATH = os.getenv("METADATA_PATH", "/faiss/data/kfood_metadata.json")

# 전역 변수로 인덱스와 메타데이터를 저장
FAISS_INDEX: Optional[faiss.Index] = None
METADATA_MAP: Dict[int, Dict[str, Any]] = {}


class VectorSearchRequest(BaseModel):
    query_vector: List[float]
    k: int = 5

class CandidateItem(BaseModel):
    id: int
    name: str
    spicy_level: int
    main_ingredients: str
    image_url: str 

def create_mock_index(d: int = 1024, nb: int = 800):
    """실제 파일 로드 실패 시 메모리 내에 더미 인덱스를 생성합니다."""
    global FAISS_INDEX, METADATA_MAP
    
    # 더미 FAISS Index 생성 (데이터 스펙 800개 x 1024차원 사용)
    xb = np.random.random((nb, d)).astype('float32')
    FAISS_INDEX = faiss.IndexFlatL2(d)
    FAISS_INDEX.add(xb)
    
    # 더미 Metadata 생성
    for i in range(FAISS_INDEX.ntotal):
        METADATA_MAP[i] = {
            "id": i,
            "name": f"한식후보_{i}",
            "spicy_level": i % 5,
            "main_ingredients": f"재료_{i}",
            "image_url": "https://placehold.co/150x150/000000/white?text=MOCK"
        }
    print(f"INFO: Generated MOCK FAISS Index with {nb} vectors.")

def load_faiss_data():
    global FAISS_INDEX, METADATA_MAP

    data_loaded_successfully = False
    with suppress(Exception):
        # 인덱스 로드
        FAISS_INDEX = faiss.read_index(FAISS_INDEX_PATH)
        
        # 메타데이터 로드
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            raw_metadata = json.load(f)
            # 메타데이터를 ID를 키로 하는 맵으로 변환
            METADATA_MAP = {item['id']: item for item in raw_metadata}
        
        print(f"INFO: Successfully loaded actual FAISS data. Total vectors: {FAISS_INDEX.ntotal}")
        data_loaded_successfully = True

    if not data_loaded_successfully:
        # 로드 실패 시 Mock 인덱스 생성 
        print("WARNING: Failed to load actual FAISS data. Creating MOCK Index for testing.")
        # 팀원의 스펙(1024차원)을 사용하여 Mock 인덱스 생성
        create_mock_index(d=1024, nb=300)


# 서버 시작 시 데이터 로드 함수 실행
@app.on_event("startup")
async def startup_event():
    load_faiss_data()


@app.post("/search", response_model=List[CandidateItem])
async def search_vectors(request: VectorSearchRequest):
    """
    입력 벡터를 받아 FAISS 인덱스에서 가장 유사한 K개의 벡터를 검색합니다.
    """
    if FAISS_INDEX is None or not METADATA_MAP:
        raise HTTPException(status_code=503, detail="FAISS Index is not loaded or mocked.")

    try:
        # NumPy 배열로 변환 및 형태 조정
        query_vector = np.array(request.query_vector).astype('float32').reshape(1, -1)
        k = min(request.k, FAISS_INDEX.ntotal) # k가 전체 벡터 수를 넘지 않도록 제한
        
        # 1. FAISS 검색 실행 (D: 거리, I: 인덱스 ID)
        D, I = FAISS_INDEX.search(query_vector, k)
        
        results = []
        for index_id in I[0]:
            if index_id >= 0 and index_id in METADATA_MAP:
                # 2. 메타데이터와 결합하여 반환
                results.append(CandidateItem(**METADATA_MAP[index_id]))
                
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")