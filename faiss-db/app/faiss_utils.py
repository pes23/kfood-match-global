# faiss-db/app/faiss_utils.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np
import faiss
import json
import os

# FastAPI 인스턴스 초기화
app = FastAPI(title="FAISS DB Vector Search API", version="1.0")

# K8s 환경 변수에서 데이터 경로를 가져옴. 
# Deployment YAML에서 PV 마운트 경로로 주입.
# (PV/PVC 미사용 시 이 경로에 파일이 없습니다.)
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/mnt/data/kfood_faiss_index.bin")
METADATA_PATH = os.getenv("METADATA_PATH", "/mnt/data/kfood_metadata.json")

# 전역 변수로 인덱스와 메타데이터를 저장
FAISS_INDEX: Optional[faiss.Index] = None
METADATA_MAP: Dict[int, Dict[str, Any]] = {}


# Pydantic 모델

class VectorSearchRequest(BaseModel):
    """검색 요청을 위한 입력 벡터"""
    query_vector: List[float]
    k: int = 5

class CandidateItem(BaseModel):
    """검색 결과로 반환될 후보 아이템 (메타데이터 포함)"""
    id: int
    name: str
    spicy_level: int
    main_ingredients: str # 메타데이터에 포함되어야 함
    image_url: str # 메타데이터에 포함되어야 함


# 서버 시작 시 실행 로직 (인덱스 로드)

def create_mock_index(d: int = 100, nb: int = 300):
    """파일 로드 실패 시 메모리 내에 더미 인덱스를 생성"""
    global FAISS_INDEX, METADATA_MAP
    
    # 더미 FAISS Index 생성
    xb = np.random.random((nb, d)).astype('float32')
    FAISS_INDEX = faiss.IndexFlatL2(d)
    FAISS_INDEX.add(xb)
    
    # 더미 Metadata 생성
    for i in range(nb):
        METADATA_MAP[i] = {
            "id": i,
            "name": f"한식후보_{i}",
            "spicy_level": i % 5,
            "main_ingredients": f"재료_{i}",
            "image_url": f"url_{i}"
        }
    print(f"INFO: Generated MOCK FAISS Index with {nb} vectors.")


def load_faiss_data():
    """
    1. PV 마운트 경로 시도 2. 실패 시 Mock 생성
    """
    global FAISS_INDEX, METADATA_MAP

    try:
        # --- 1. 실제 PV/PVC 마운트 경로 시도 ---
        
        # 인덱스 로드
        FAISS_INDEX = faiss.read_index(FAISS_INDEX_PATH)
        
        # 메타데이터 로드
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            raw_metadata = json.load(f)
            # 메타데이터는 리스트일 수 있으므로 ID를 키로 하는 맵으로 변환
            METADATA_MAP = {item['id']: item for item in raw_metadata}
        
        print(f"INFO: Successfully loaded actual FAISS data. Total vectors: {FAISS_INDEX.ntotal}")

    except Exception as e:
        # --- 2. 로드 실패 시 Mock 인덱스 생성 ---
        print(f"WARNING: Failed to load actual FAISS data ({e}). Creating MOCK Index.")
        create_mock_index()
        

# 서버 시작 시 데이터 로드 함수 실행
@app.on_event("startup")
async def startup_event():
    load_faiss_data()


@app.post("/search", response_model=List[CandidateItem])
async def search_vectors(request: VectorSearchRequest):
    """
    입력 벡터를 받아 FAISS 인덱스에서 가장 유사한 K개의 벡터를 검색합니다.
    """
    if FAISS_INDEX is None:
        # Mock 생성도 실패했을 경우 비정상 서비스 종료
        raise HTTPException(status_code=503, detail="FAISS Index is not loaded or mocked.")

    try:
        # NumPy 배열로 변환 및 형태 조정
        query_vector = np.array(request.query_vector).astype('float32').reshape(1, -1)
        k = request.k
        
        # 1. FAISS 검색 실행
        # I: 인덱스 배열 (가장 가까운 K개의 ID)
        D, I = FAISS_INDEX.search(query_vector, k)
        
        results = []
        for index_id in I[0]:
            if index_id in METADATA_MAP:
                # 2. 메타데이터와 결합하여 반환
                results.append(CandidateItem(**METADATA_MAP[index_id]))
                
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")