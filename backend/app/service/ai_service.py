# app/service/ai_service.py

from typing import List, Dict, Any

def generate_food_profile(foreign_food: str) -> str:
    return "Dummy profile text"

def generate_justification(food_profile, candidates, foreign_food) -> List[Dict[str, Any]]:
    return candidates