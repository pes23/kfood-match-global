from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
import os
import logging
import uvicorn

# 1. 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("translate-service")

app = FastAPI(title="K-Food Translate Service (Gemini)")

# 2. Gemini 클라이언트 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini Client for Translation initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}")
else:
    logger.warning("GEMINI_API_KEY not found. Falling back to Mock mode.")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "ko"   # 기본값 한국어

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    service_mode: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/translate", response_model=TranslationResponse)
async def translate_text_endpoint(request: TranslationRequest):
    """
    Gemini를 이용한 실제 번역 API 엔드포인트
    """
    logger.info(f"Translation Request: '{request.text}' -> {request.target_lang}")
    
    # 1. Mock 모드 (API 키 없을 때)
    if not client:
        return TranslationResponse(
            original_text=request.text,
            translated_text=f"[Mock/{request.target_lang}] {request.text}",
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            service_mode="mock"
        )

    # 2. 실제 Gemini 번역 요청
    try:
        # 번역 전용 프롬프트
        prompt = (
            f"You are a professional translator. Translate the following text into {request.target_lang} language code. "
            f"Only output the translated text, nothing else.\n\nText: {request.text}"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        translated_text = response.text.strip()
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            service_mode="gemini-real"
        )

    except Exception as e:
        logger.error(f"Gemini translation failed: {e}")
        # 에러 발생 시 원본 반환 (서비스 중단 방지)
        return TranslationResponse(
            original_text=request.text,
            translated_text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            service_mode="error-fallback"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)