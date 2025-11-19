# translate-service/app/translate_app.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# FastAPI 인스턴스 초기화
app = FastAPI(title="Translate Service API", version="1.0")

# Pydantic 모델 정의
class TranslationRequest(BaseModel):
    """번역 요청을 위한 입력 데이터"""
    text: str              
    target_lang: str = "en" 

class TranslationResponse(BaseModel):
    """번역 결과 응답"""
    translated_text: str

# 번역 로직 (Mock 구현)
def mock_translate(text: str, target_lang: str) -> str:
    """
    Mock 번역 로직: 실제 API 호출 없이 더미 결과를 반환.
    """
    if target_lang == "en":
        return f"[EN Translation Mock] The reason is that the texture is chewy."
    elif target_lang == "es":
        return f"[Traducción Simulación] La razón es que la textura es masticable."
    else:
        # 최종 번역 결과 텍스트를 그대로 반환한다고 가정
        return f"[Translation Mock ({target_lang})] Reason for: {text}"


@app.post("/translate", response_model=TranslationResponse)
async def translate_text_endpoint(request: TranslationRequest):
    """
    텍스트를 받아 지정된 언어로 번역 결과를 반환하는 엔드포인트.
    """
    try:
        translated = mock_translate(request.text, request.target_lang)
        
        return TranslationResponse(translated_text=translated)

    except Exception as e:
        # K8s 내부 서비스 문제 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail=f"Translation failure: {e}")