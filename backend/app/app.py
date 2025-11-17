# app/app.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx

# --- 서비스 파일 임포트 (Mock 함수만 남기고 모두 제거) ---
# 실제 로직은 건너뛰고 Mock 데이터로 대체
from app.service.ai_service import generate_food_profile, generate_justification 
from app.service.faiss_client import search_faiss_api, generate_embedding 

# Pydantic 모델 정의 (프론트엔드 연동)
class RecommendationItem(BaseModel):
    name: str
    spicy_level: int
    main_ingredients: str
    reason: str
    image_url: str

class RecommendationResponse(BaseModel):
    input_food: str
    items: List[RecommendationItem]

# FastAPI 초기화 및 CORS 설정
app = FastAPI(title="K-Food Match Backend API (Front-end Dev Mock)")

origins = ["http://localhost:3000"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# MOCK DATA 정의 (하드코딩)
# ----------------------------------------------------
MOCK_FINAL_RESPONSE = RecommendationResponse(
    input_food="Tacos",
    items=[
        RecommendationItem(
            name="김치전",
            spicy_level=3,
            main_ingredients="김치, 밀가루",
            reason="타코의 짭짤하고 바삭한 식감을 전이 대체하며, 김치의 매콤함이 좋은 대안이 됩니다.",
            image_url="https://placehold.co/150x150/FF6347/white?text=Kimchi+Jeon"
        ),
        RecommendationItem(
            name="크림 떡볶이",
            spicy_level=1,
            main_ingredients="떡, 크림 소스",
            reason="부드러운 크림 베이스와 쫄깃한 떡의 식감이 타코 속재료의 농후함을 대체합니다.",
            image_url="https://placehold.co/150x150/ADD8E6/white?text=Cream+Tteok"
        )
    ]
)

# /recommend 엔드포인트 구현
@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_kfood(
    foreign_food: str = Query(..., description="사용자가 입력한 외국 음식 이름")
):
    """
    [FRONT-END MOCK] 모든 AI 및 DB 호출을 건너뛰고 하드코딩된 JSON 응답을 반환합니다.
    """
    
    try:
        # 모든 복잡한 비동기/AI 호출 로직을 건너뛰고 Mock 데이터를 반환합니다.
        
        # 입력 음식 이름만 응답에 반영
        response = MOCK_FINAL_RESPONSE.model_copy(
            update={"input_food": foreign_food}
        )
        
        # 200 OK 응답 반환
        return response

    except Exception as e:
        # 만약 Mock 응답 반환 중에도 오류가 난다면 심각한 Python 문제입니다.
        raise HTTPException(status_code=500, detail=f"MOCK SERVER FAILED: {e}")