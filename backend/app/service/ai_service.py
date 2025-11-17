# app/service/ai_service.py
import os
from google import genai
from google.genai import types
from typing import List, Dict, Any

GEMINI_MODEL = "gemini-2.5-flash"

def generate_food_profile(client: genai.Client, foreign_food: str) -> str:
    prompt = (
        f"다음 외국 음식 '{foreign_food}'를 맛, 식감, 주요 재료, 조리법의 네 가지 관점에서 "
        "구체적으로 분석하고 설명하는 텍스트를 생성해줘. 답변 외 불필요한 서문은 제거해."
    )
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            temperature=0.7
        )
    )
    return response.text

def generate_justification(
    client: genai.Client,
    input_profile: str, 
    candidates: List[Dict[str, Any]], 
    foreign_food: str
) -> List[Dict[str, Any]]:
    """
    FAISS 결과와 프로파일을 바탕 최종 추천 이유 생성.
    """
    if clientT is None:
        return candidates
        
    candidate_list_text = "\n".join(
        [f"- {item['name']}: 맛={item['spicy_level']}단계, 재료={item['main_ingredients']}" for item in candidates]
    )

    prompt = (
        f"사용자의 입력 음식 '{foreign_food}'의 특징은 다음과 같다:\n[특징: {input_profile}]\n"
        f"다음 한국 음식 후보군 중에서 가장 유사한 2가지를 선정하고, "
        "선정된 음식별로 외국 음식의 특징과 어떤 점에서 공통점과 유사성이 있는지(맛, 식감 기준) "
        "100자 이내로 자연스럽게 설명해줘. 답변은 오직 텍스트로만 해."
        f"\n[한국 음식 후보군]:\n{candidate_list_text}"
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            temperature=0.5
        )
    )
    
    full_reason_text = response.text
    
    results = []
    for item in candidates:
        # 실제로는 생성한 이유 텍스트를 파싱하여 여기에 할당해야 함
        item['reason'] = full_reason_text 
        # 문제점 보완: spicy_level/image_url 빈 값 처리 로직 유지
        if item.get('spicy_level') is None or item.get('spicy_level') == "":
             item['spicy_level'] = 0
        if item.get('image_url') is None or item.get('image_url') == "":
             item['image_url'] = "https://example.com/default_kfood.png"

        results.append(item)
    
    return results