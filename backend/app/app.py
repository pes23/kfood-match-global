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



# =========================================
# 🔥 텍스트 필드 전체 번역 함수 (주석 유지)
# =========================================
async def translate_item_fields(item: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
    """
    item(dict) 안의 name, main_ingredients, reason을 target_lang으로 번역 후 덮어쓴다.
    (name_en 대신 name 사용)
    """

    # 🌶 name_en → 사용자 언어 name 변환
    name_en = item.get("name_en", "")
    if name_en:
        translated_name = await translate_text(name_en, target_lang)
        item["name"] = translated_name
    else:
        # name_en 없으면 한국어 이름이라도 name에 넣기
        item["name"] = item.get("name_ko", "Unknown")

    # main_ingredients, reason 번역
    fields = ["main_ingredients", "reason"]
    for field in fields:
        text = item.get(field, "")
        if text:
            translated = await translate_text(text, target_lang)
            item[field] = translated

    return item


async def translate_full_items(items: List[Dict[str, Any]], target_lang: str):
    tasks = [translate_item_fields(item, target_lang) for item in items]
    return await asyncio.gather(*tasks)



# =========================================
# /recommend 엔드포인트 구현 (주석 그대로 유지)
# =========================================
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
        
        # ingredients 문자열 통합 (번역 전에 처리)
        for item in justified_items_dicts:
            if isinstance(item.get("ingredients"), list):
                item["main_ingredients"] = ", ".join(item["ingredients"])
            elif isinstance(item.get("ingredients"), str):
                item["main_ingredients"] = item["ingredients"]

        # 전체 필드를 사용자 입력 언어로 번역
        translated_items = await translate_full_items(justified_items_dicts, target_lang=source_lang)

        
        # 6. Dict -> Pydantic Model 변환
        final_items = []
        for item in translated_items:

            # 🔥 음식 이름 우선순위 (name → name_en → name_ko)
            # name: 이미 사용자 언어로 번역됨
            translated_name = item.get("name")
            name_en = item.get("name_en")
            name_ko = item.get("name_ko")

            # ⭐ 한국어 병기 규칙
            if source_lang == "ko":
                # 한국어 사용자 → 한국어 이름 우선
                name_value = name_ko or translated_name or name_en or "Unknown"
            else:
                # 외국인 사용자 → name (사용자언어) + 한국어 병기
                if name_ko:
                    name_value = f"{translated_name} ({name_ko})"
                else:
                    name_value = translated_name or name_en or "Unknown"

            ingredients_str = item.get('main_ingredients', '')

            final_items.append(
                RecommendationItem(
                    name=name_value,
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
