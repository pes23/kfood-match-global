#FastAPI 인스턴스 및 /recommend 엔드포인트 설정
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

# 로컬 모듈 임포트
from app.service.ai_service import generate_food_profile, generate_justification
from app.service.faiss_client import search_faiss_api, generate_embedding 

# ----------------------------------------------------
# 1. Pydantic 모델 정의 (프론트엔드 연동)
# ----------------------------------------------------

class RecommendationItem(BaseModel):
    name: str
    spicy_level: int
    main_ingredients: str
    reason: str
    image_url: str

class RecommendationResponse(BaseModel):
    input_food: str
    items: List[RecommendationItem]

# ----------------------------------------------------
# 2. FastAPI 초기화 및 CORS 설정
# ----------------------------------------------------

app = FastAPI(title="K-Food Match Backend API")

origins = ["http://localhost:3000"] # Next.js 개발 환경
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 3. 핵심 엔드포인트
# ----------------------------------------------------

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_kfood(
    foreign_food: str = Query(..., description="사용자가 입력한 외국 음식 이름")
):
    """
    외국 음식 이름을 기반으로 K-푸드를 추천하고 상세 근거를 반환하는 엔드포인트.
    """
    
    try:
        # --- 1. GPT 음식 특징 생성 (Mock) ---
        food_profile = generate_food_profile(foreign_food)

        # --- 2. 임베딩 벡터 생성 (Mock) ---
        profile_vector = await generate_embedding(food_profile)
        
        # --- 3. FAISS 검색 구현 (Mock 통신) ---
        # FAISS Pod에 벡터를 보내 유사한 K-푸드 후보군(메타데이터 포함)을 요청
        candidate_items = await search_faiss_api(profile_vector, k=5)
        
        # --- 4. GPT 유사성 설명 생성 (Mock) ---
        # 후보군에 대한 추천 이유를 생성하여 items에 'reason' 필드를 추가
        final_items = generate_justification(candidate_items, food_profile, foreign_food)
        
        # --- 5. 최종 번역 (Translate Service 호출 로직이 여기에 삽입됨) ---
        # (번역 서비스 클라이언트가 구현되면 이 위치에서 최종 번역을 수행)

        # --- 6. JSON 응답 구성 ---
        return RecommendationResponse(
            input_food=foreign_food,
            items=final_items
        )

    except httpx.RequestError as e:
        # FAISS나 Translate Service와의 통신 오류 처리
        raise HTTPException(
            status_code=503, 
            detail=f"Service unavailable: Internal communication failed ({e})"
        )
    except Exception as e:
        # 일반적인 서버 오류 처리
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# ----------------------------------------------------
# 4. 서버 실행 안내
# ----------------------------------------------------
# 로컬 실행: uvicorn app.main:app --reload --app-dir app
```eof

#이 코드를 통해 팀원이 FAISS 파일을 넘겨주면 `generate_embedding`과 `search_faiss_api` 함수 내부의 Mock 로직만 실제 API 호출로 대체하면 됩니다.