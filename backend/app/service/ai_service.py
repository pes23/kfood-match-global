# app/service/ai_service.py
import os
from google import genai
from google.genai import types
from typing import List, Dict, Any
import asyncio
import time

GEMINI_MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
INITIAL_DELAY = 2

def generate_food_profile(client: genai.Client, standard_food_input: str) -> str:
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
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_DELAY * (attempt + 1)
                print(f"WARNING: Gemini food profile generation failed (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay}s. Error: {e}")
                time.sleep(delay)
            else:
                print(f"FATAL ERROR: Gemini food profile generation failed after {MAX_RETRIES} attempts. Last Error: {e}")
                raise e
    
    raise Exception("Failed to generate food profile after retries.")

def generate_justification_sync(
    client: genai.Client,
    input_profile: str, 
    candidates: List[Dict[str, Any]], 
    standard_food_input: str
) -> List[Dict[str, Any]]:
    """
    FAISS 결과와 프로파일을 바탕 최종 추천 이유 생성.
    """
    if client is None:
        return candidates
        
    candidate_list_text = "\n".join(
        [f"- {item['name']}: 맛={item['spicy_level']}단계, 재료={item['main_ingredients']}" for item in candidates]
    )

    prompt = (
        f"Using the input food '{standard_food_input}' profile below:\n[Profile: {input_profile}]\n"
        f"Select the 2 most similar Korean food candidates and explain the similarities (taste, texture) "
        f"in English, concisely (max 100 words). The output must only be the explanation text."
        f"\n[Korean Candidates]:\n{candidate_list_text}"
    )

    for attempt in range(MAX_RETRIES):
        try:
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
                item['reason'] = full_reason_text 
                # 빈 값 처리 로직
                if item.get('spicy_level') is None or item.get('spicy_level') == "":
                     item['spicy_level'] = 0
                if item.get('image_url') is None or item.get('image_url') == "":
                     item['image_url'] = "https://example.com/default_kfood.png"
        
                results.append(item)
            
            return results
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_DELAY * (attempt + 1)
                print(f"WARNING: Gemini justification generation failed (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay}s. Error: {e}")
                time.sleep(delay)
            else:
                print(f"FATAL ERROR: Gemini justification generation failed after {MAX_RETRIES} attempts. Last Error: {e}")
                raise e

    raise Exception("Failed to generate justification after retries.")

async def generate_justification(
    client: genai.Client,
    input_profile: str, 
    candidates: List[Dict[str, Any]], 
    standard_food_input: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        generate_justification_sync, client, input_profile, candidates, standard_food_input
    )