#FAISS Pod 통신 클라이언트
import httpx
from typing import List, Dict, Any
# K8s 내부 DNS 이름 사용.
FAISS_SERVICE_URL = "http://faiss-db-service:8001" 
# Mock 데이터를 위한 임시 메타데이터
MOCK_METADATA = [
    {"id": 1, "name": "크림 떡볶이", "spicy_level": 1, "main_ingredients": "떡, 크림 소스", "image_url": "url_to_cream_tteok"},
    {"id": 2, "name": "김치전", "spicy_level": 3, "main_ingredients": "김치, 밀가루", "image_url": "url_to_kimchi_jeon"},
]
async def search_faiss_api(profile_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
    """
    FAISS DB Pod의 /search 엔드포인트에 벡터 검색을 요청하는 Mock 함수.
    실제 구현 시에는 httpx를 사용하여 FAISS_SERVICE_URL로 POST 요청을 보내야 합니다.
    """
    print(f"DEBUG: Searching FAISS API at {FAISS_SERVICE_URL} (MOCK)")
    
    # 팀원이 벡터를 생성할 때 사용할 임베딩 모델의 차원과 일치하는 
    # Mock 벡터를 생성하거나, 여기서 벡터 생성 단계를 임시로 건너뜁니다.
    
    # Mock 응답: 상위 2개 후보를 메타데이터와 결합하여 반환
    results = []
    
    # 팀원에게 받은 메타데이터를 사용하여 실제 데이터 형태를 시뮬레이션
    results.append(MOCK_METADATA[0]) 
    results.append(MOCK_METADATA[1])
    
    return results

async def generate_embedding(profile_text: str) -> List[float]:
    """
    입력 음식 프로파일 텍스트를 임베딩 벡터로 변환하는 Mock 함수.
    실제 구현 시에는 OpenAI/Gemini 임베딩 API를 호출해야 합니다.
    """
    print("DEBUG: Generating embedding vector (MOCK)")
    # 임시로 100차원 벡터를 반환한다고 가정합니다.
    return [0.5] * 100