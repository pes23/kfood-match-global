# backend/app/service/translate_client.py
import httpx
from typing import List, Dict, Any
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

# K8s 내부 DNS 이름을 사용. 환경 변수가 없으면 Docker Compose 기본 포트
TRANSLATE_SERVICE_URL = os.getenv("TRANSLATE_SERVICE_URL", "http://translate-service:8000")


# 1. 최종 번역 요청 (실제 httpx 통신)
async def translate_text(text: str, target_lang: str) -> str:
    """
    Translate Service Pod에 단일 텍스트 번역을 요청.
    이 함수는 사용자 입력(foreign_food)을 영어로 번역하거나,
    최종 결과(reason)를 한국어로 번역하는 데 사용됩니다.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{TRANSLATE_SERVICE_URL}/translate",
                json={"text": text, "target_lang": target_lang}
            )
            response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 처리
            
            # 응답에서 'translated_text' 키를 찾아 반환
            return response.json().get("translated_text", text)
            
    except httpx.RequestError as e:
        logger.error(f"Translation Service connection error to {TRANSLATE_SERVICE_URL}: {e}")
        # 연결 실패 시 원본 텍스트를 그대로 반환 (최악의 경우 fallback)
        return text 
    except Exception as e:
        logger.error(f"Translation Service failed to process response: {e}")
        return text
    

# 2. 결과 리스트의 'reason' 필드 번역 (비동기 병렬 처리)
async def translate_results_async(items: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
    """
    추천 결과 리스트를 받아 'reason' 필드를 target_lang으로 번역합니다.
    (현재는 Gemini가 이유를 한국어로 생성하므로, 이 함수는 거의 사용되지 않을 수 있습니다.)
    """
    
    async def translate_single_reason(item: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        reason_text = item.get('reason', '')
        
        # 실제 번역 API 호출
        translated_reason = await translate_text(reason_text, target_lang)
        
        item['reason'] = translated_reason
        return item
    
    # 모든 항목에 대해 병렬로 번역 작업을 시작합니다.
    tasks = [translate_single_reason(item, target_lang) for item in items]
    
    return await asyncio.gather(*tasks)