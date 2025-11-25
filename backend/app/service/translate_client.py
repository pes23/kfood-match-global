# backend/app/service/translate_client.py
import httpx
from typing import List, Dict, Any
import os

# K8s 내부 DNS 이름을 사용.
TRANSLATE_SERVICE_URL = os.getenv("TRANSLATE_SERVICE_URL", "http://translate-service:8000")
#TRANSLATE_SERVICE_URL = "http://localhost:8002" #테스트용

# 1. 입력 언어 감지 및 표준 언어 변환 (Mock)
async def detect_and_translate_input(foreign_food: str, target_lang: str = "en") -> tuple[str, str]:
    """
    사용자 입력 텍스트의 언어를 감지하고 표준 언어(영어)로 번역. (Mock)
    """
    # 스페인어/영어 시뮬레이션
    if "tacos" in foreign_food.lower() or "burrito" in foreign_food.lower():
        # 스페인어로 가정하고, 번역된 표준어와 원본 언어 코드를 반환
        return "Tacos", "es" 
    
    # 기본값: 영어로 가정
    return foreign_food, "en" 

# 2. 최종 번역 요청 (실제 httpx 통신)
async def translate_text(text: str, target_lang: str) -> str:
    """
    Translate Service Pod에 단일 텍스트 번역을 요청.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            f"{TRANSLATE_SERVICE_URL}/translate",
            json={"text": text, "target_lang": target_lang}
        )
        response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 처리
        
        return response.json().get("translated_text", text)


async def translate_results_async(items: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
    """
    추천 결과 리스트를 받아 'reason' 필드 번역.
    """
    translated_items = []
    
    for item in items:
        # 'reason' 필드만 번역.
        reason_text = item.get('reason', '')
        
        # 실제 번역 API 호출
        translated_reason = await translate_text(reason_text, target_lang)
        
        item['reason'] = translated_reason
        translated_items.append(item)
        
    return translated_items