# -*- coding: utf-8 -*-
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx
from google import genai 
import asyncio
import os
import logging
from langdetect import detect, DetectorFactory

from app.service.ai_service import generate_food_profile, generate_justification, generate_embedding
from app.service.faiss_client import search_faiss_api
from app.service.translate_client import translate_text, translate_results_async

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BackendApp")

try:
    api_key = os.getenv("GEMINI_API_KEY")

    logger.info(f"DEBUG: Retrieved GEMINI_API_KEY length: {len(api_key.strip()) if api_key else 0}")
    if not api_key or not api_key.strip():
        raise ValueError("GEMINI_API_KEY environment variable is missing or empty. Cannot initialize client.")

    GEMINI_SYNC_CLIENT = genai.Client(api_key=api_key)
    logger.info("INFO: Gemini Client initialized successfully.")

except Exception as e:
    logger.error(f"FATAL WARNING: Failed to initialize Gemini Client. Check API Key. Error: {e}")
    GEMINI_SYNC_CLIENT = None

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

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "backend-gateway"}

# /recommend 엔드포인트 구현
@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_kfood(
    foreign_food: str = Query(..., description="사용자가 입력한 외국 음식 이름")
):
    
    if GEMINI_SYNC_CLIENT is None:
        raise HTTPException(status_code=500, detail="Internal Server Error: Gemini Client Not Initialized. Check API Key.")
    
    try:
        #입력 언어 감지
        DetectorFactory.seed = 0  # langdetect 일관성 보장
        source_lang = detect(foreign_food)
        logger.info(f"Detected input language: {source_lang}")
        #표준 언어(영어) 변환
        if source_lang != "en":
            standard_input = await translate_text(foreign_food, target_lang="en")
            if standard_input == foreign_food:
                logger.info(f"Translation fallback: input remains '{foreign_food}'")
        else:
            standard_input = foreign_food

        logger.info(f"Standard input for Gemini: '{standard_input}'")

        # Gemini 음식 프로필 생성
        food_profile = await asyncio.to_thread(
            generate_food_profile, GEMINI_SYNC_CLIENT, standard_input
        )
        logger.info("Food profile generated.")

        # Embedding 벡터 생성
        profile_vector = await generate_embedding(GEMINI_SYNC_CLIENT, food_profile)
        
        # FAISS 검색 
        candidate_items: List[Dict[str, Any]] = await search_faiss_api(profile_vector, k=2)
        
        if not candidate_items:
            logger.warning("No candidates found from FAISS.")
            return RecommendationResponse(input_food=foreign_food, items=[])

        # Gemini 유사성 설명 생성
        justified_items_dicts: List[Dict[str, Any]] = await generate_justification(
            GEMINI_SYNC_CLIENT, food_profile, candidate_items, standard_input
        )
        
        # 이유 번역
        translated_items_dicts = await translate_results_async(justified_items_dicts, target_lang=source_lang)
        
        # 6. Dict -> Pydantic Model 변환
        final_items = []
        for item in translated_items_dicts:
            ingredients_str = item.get('main_ingredients', '')
            if isinstance(item.get('ingredients'), list):
                 ingredients_str = ", ".join(item['ingredients'])
            elif isinstance(item.get('ingredients'), str):
                 ingredients_str = item['ingredients']

            final_items.append(
                RecommendationItem(
                    name=item.get('name_en', 'Unknown'),
                    spicy_level=int(item.get('spicy_level', 0)),
                    main_ingredients=ingredients_str,
                    reason=item.get('reason', ''),
                    image_url=item.get('image_url', '')
                )
            )
        
        return RecommendationResponse(
            input_food=foreign_food,
            items=final_items
        )

    except httpx.RequestError as e:
        logger.error(f"Service communication error: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"Service unavailable: Internal communication failed (FAISS/Translate Service)."
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")