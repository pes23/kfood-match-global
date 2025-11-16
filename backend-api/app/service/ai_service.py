#GPT 특징/설명 생성 서비스  
from typing import List, Dict, Any
# Mock 데이터 구조를 위한 임시 정의
MOCK_FOOD_PROFILE = "맛: 부드럽고 짭짤하며 치즈 맛이 강함. 식감: 쫄깃하고 탄력 있음. 조리법: 끓이거나 볶음."
MOCK_REASON_TEMPLATE = "추천 음식 {}는 {}과/와 같은 {} 맛을 가지며, {} 식감이 유사합니다."

def generate_food_profile(foreign_food: str) -> str:
    """
    GPT를 호출하여 입력 음식의 특징 분석 텍스트를 생성하는 Mock 함수.
    실제 구현 시에는 OpenAI/Gemini API를 호출하여 정성적 특징을 생성해야 합니다.
    """
    print(f"DEBUG: Generating profile for '{foreign_food}' (MOCK)")
    return MOCK_FOOD_PROFILE

def generate_justification(
    input_profile: str, 
    candidates: List[Dict[str, Any]], 
    foreign_food: str
) -> List[Dict[str, Any]]:
    """
    GPT를 호출하여 각 후보 한국 음식에 대한 추천 이유를 생성하는 Mock 함수.
    """
    print(f"DEBUG: Generating justification based on {len(candidates)} candidates (MOCK)")
    
    # Mock 데이터에 추천 이유를 추가하여 반환
    results = []
    for item in candidates:
        reason_text = MOCK_REASON_TEMPLATE.format(
            item['name'], 
            foreign_food, 
            "부드러운", # 임시 이유
            "쫄깃한"    # 임시 이유
        )
        item['reason'] = reason_text
        results.append(item)
    
    return results