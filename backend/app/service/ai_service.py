import os
from google import genai
from google.genai import types
from typing import List, Dict, Any
import asyncio
import time
import logging
import numpy as np 

# 로거 설정
logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "text-embedding-004" 
MAX_RETRIES = 3
INITIAL_DELAY = 2

def generate_food_profile(client: genai.Client, standard_food_input: str) -> str:
    """음식 특징 분석 텍스트 생성"""
    prompt = (
        f"Analyze the foreign food '{standard_food_input}' based on these four criteria: "
        "taste, texture, main ingredients, and cooking method. "
        "Generate a descriptive text analysis. Eliminate unnecessary preamble in the response. "
    )
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(temperature=0.7)
            )
            return response.text
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_DELAY * (attempt + 1)
                logger.warning(f"Gemini food profile generation failed (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay}s. Error: {e}")
                time.sleep(delay)
            else:
                logger.error(f"FATAL ERROR: Gemini food profile generation failed after {MAX_RETRIES} attempts. Last Error: {e}")
                raise e
            
    raise Exception("Failed to generate food profile after retries.")

def generate_justification_sync(
    client: genai.Client,
    input_profile: str, 
    candidates: List[Dict[str, Any]], 
    standard_food_input: str
) -> List[Dict[str, Any]]:
    """추천 이유 생성 (각 후보별 개별 생성으로 수정)"""
    if client is None or not candidates:
        return candidates
    
    results = []
    
    for candidate in candidates:
        food_name = candidate.get('name_en', candidate.get('name_ko', 'Unknown Food'))
        
        # 1. 현재 후보 음식에 대한 정보로 프롬프트 구성
        candidate_info = (
            f"- {food_name}: Spicy={candidate.get('spicy_level', 0)}, "
            f"Ingredients={candidate.get('main_ingredients', '')}"
        )
        
        prompt = (
            f"Analyze the culinary connection between the input food '{standard_food_input}' "
            f"(Profile: {input_profile}) and the recommended Korean food '{food_name}'.\n"
            f"Explain the common gastronomic reasons (e.g., shared taste, texture, or ingredients) "
            f"why '{food_name}' is recommended as a pair for '{standard_food_input}'. "
            f"Write a concise explanation in English (max 60 words). The output must only be the explanation text."
            f"\n[Recommended Korean Food Details]:\n{candidate_info}"
        )

        # 2. 각 후보에 대해 Gemini 호출 및 재시도 로직 적용
        reason_text = ""
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[prompt],
                    config=types.GenerateContentConfig(temperature=0.5)
                )
                reason_text = response.text
                break # 성공 시 루프 탈출
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    delay = INITIAL_DELAY * (attempt + 1)
                    logger.warning(f"Gemini justification generation failed for {food_name} (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay}s. Error: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"FATAL ERROR: Gemini justification generation failed for {food_name} after {MAX_RETRIES} attempts. Last Error: {e}")
                    reason_text = f"Failed to generate reason for {food_name}."
                    break # 최종 실패 시 루프 탈출 후 기본 메시지 사용
        
        # 3. 결과 업데이트 및 빈 값 처리
        candidate['reason'] = reason_text
        
        if candidate.get('spicy_level') is None or candidate.get('spicy_level') == "":
            candidate['spicy_level'] = 0
        if candidate.get('image_url') is None or candidate.get('image_url') == "":
            candidate['image_url'] = "https://via.placeholder.com/300?text=K-Food"
            
        results.append(candidate)
            
    return results

async def generate_justification(
    client: genai.Client,
    input_profile: str, 
    candidates: List[Dict[str, Any]], 
    standard_food_input: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        generate_justification_sync, client, input_profile, candidates, standard_food_input
    )
    
async def generate_embedding(client: genai.Client, text: str) -> List[float]:
    """
    Gemini 임베딩(768차원) 생성 후 1024차원으로 패딩(Padding).
    """
    if not text:
        return []

    # 동기 함수를 비동기로 래핑
    def _get_embedding_sync():
        for attempt in range(MAX_RETRIES):
            try:
                result = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=text
                )
                return result.embeddings[0].values
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(INITIAL_DELAY)
                else:
                    logger.error(f"Gemini embedding failed: {e}")
                    raise e
            
    try:
        embedding = await asyncio.to_thread(_get_embedding_sync)
        
        # [중요] 1024차원 보정 로직 (Zero Padding)
        current_dim = len(embedding)
        target_dim = 1024
        
        if current_dim < target_dim:
            padding = [0.0] * (target_dim - current_dim)
            embedding.extend(padding)
            logger.info(f"Embedding padded from {current_dim} to {target_dim} dimensions.")
        elif current_dim > target_dim:
            embedding = embedding[:target_dim]
            
        return embedding

    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        # 에러 시 0 벡터 반환 (서버 다운 방지)
        return [0.0] * 1024