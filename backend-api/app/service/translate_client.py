# backend-api/app/service/translate_client.py
import httpx
from typing import Optional

# K8s 내부 DNS 이름 및 포트 (Dockerfile.translate에서 EXPOSE 8002 설정 가정)
TRANSLATE_SERVICE_URL = "http://translate-service:8002/translate"

async def translate_text(text: str, target_lang: str) -> str:
    """
    내부 Translate Service Pod에 번역 요청을 보냅니다.
    """
    # Translate Service는 아직 구현되지 않았으므로 Mock 응답을 반환. 
    if target_lang == "en":
        return f"MOCK TRANSLATED: The reason for recommending {text} is similar to {target_lang}."
    
    # 실제 구현 시:
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             TRANSLATE_SERVICE_URL,
    #             json={"text": text, "target_lang": target_lang}
    #         )
    #         response.raise_for_status()
    #         return response.json().get("translated_text", text)
    # except httpx.RequestError:
    #     print("ERROR: Failed to connect to Translate Service.")
    #     return text # 실패 시 원본 텍스트 반환

    return f"MOCK TRANSLATED: {text} (Target: {target_lang})"