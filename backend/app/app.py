# app/app.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx
from google import genai 
import asyncio

from app.service.ai_service import generate_food_profile, generate_justification 
from app.service.faiss_client import search_faiss_api, generate_embedding 

try:
    GEMINI_SYNC_CLIENT = genai.Client()
except Exception as e:
    print(f"FATAL WARNING: Failed to initialize Gemini Client. Check API Key. Error: {e}")
    GEMINI_SYNC_CLIENT = None
    
# 향후 번역 클라이언트를 위한 임포트 (아직 구현되지 않음)
# from app.service.translate_client import translate_results_async

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

app = FastAPI(title="K-Food Match Backend API (Gemini Ready)")

origins = ["http://localhost:3000"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /recommend 엔드포인트 구현

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_kfood(
    foreign_food: str = Query(..., description="사용자가 입력한 외국 음식 이름")
):
    try:
        # 1. Gemini 음식 특징 생성 
        food_profile = await asyncio.to_thread(
            generate_food_profile, GEMINI_SYNC_CLIENT, foreign_food
        )

        # 2. Gemini Embedding 벡터 생성 
        profile_vector = await asyncio.to_thread(
            generate_embedding, GEMINI_SYNC_CLIENT, food_profile
        )
        
        # 3. FAISS 검색 
        candidate_items: List[Dict[str, Any]] = await search_faiss_api(profile_vector, k=5)
        
        # 4. Gemini 유사성 설명 생성
        final_items: List[RecommendationItem] = await asyncio.to_thread(
            generate_justification, GEMINI_SYNC_CLIENT, food_profile, candidate_items, foreign_food
        )
        
        return RecommendationResponse(
            input_food=foreign_food,
            items=final_items
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service unavailable: Internal communication failed (FAISS/Translate Service): {e}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")