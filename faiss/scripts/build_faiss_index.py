import os
import json
import numpy as np
import pandas as pd
import faiss
from google import genai
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join("faiss", "data")

CSV_PATH = os.path.join(DATA_DIR, "kfood.csv")
EMBEDDING_NPY_PATH = os.path.join(DATA_DIR, "kfood_embeddings.npy")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "kfood_faiss.index")
METADATA_JSON_PATH = os.path.join(DATA_DIR, "kfood_metadata.json")

BATCH_SIZE = 64
MODEL_NAME = "models/text-embedding-004"

# Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_combined_text(row: pd.Series) -> str:
    name_ko = row.get("name_ko", "")
    name_en = row.get("name_en", "")
    description = row.get("description", "")
    ingredients = row.get("ingredients", "")
    category = row.get("category", "")
    spicy_level = row.get("spicy_level", "")

    text = (
        f"한국 음식 이름(한글): {name_ko}\n"
        f"한국 음식 이름(영어): {name_en}\n"
        f"카테고리: {category}\n"
        f"매운 정도: {spicy_level}\n"
        f"주요 재료: {ingredients}\n"
        f"설명: {description}"
    )
    return text


def create_embeddings(texts):
    """
    Gemini SDK의 단일 embed_content 호출을 사용하여 임베딩 생성
    (배치 기능이 지원되지 않는 SDK 버전에 대응)
    """
    all_embeddings = []

    print("✨ Creating embeddings with Gemini...")
    
    # BATCH_SIZE 로직 대신 전체 텍스트 리스트 순회
    for i, text in enumerate(texts):
        # 진행 상황 표시 (선택 사항)
        if i % 10 == 0:
             print(f" - Embedding item {i + 1}/{len(texts)}")
        
        try:
            # client.models.embed_content 사용
            res = client.models.embed_content(
                model=MODEL_NAME,
                contents=[text]  # 단일 텍스트를 content 파라미터로 전달
            )
            actual_embedding_values = res.embeddings[0].values
            # 임베딩 결과는 res.embedding.values로 접근
            all_embeddings.append(np.array(actual_embedding_values, dtype="float32"))
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to embed content for item {i}. Error: {e}")
            # 실패 시 768차원 0 벡터 추가
            all_embeddings.append(np.zeros(768, dtype="float32")) 

    embeddings = np.vstack(all_embeddings)
    print("📏 Embeddings shape:", embeddings.shape)

    return embeddings


def build_faiss_index(embeddings: np.ndarray):
    d = embeddings.shape[1]
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(d)
    index.add(embeddings)

    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"💾 Saved FAISS index → {FAISS_INDEX_PATH}")


import json

def build_metadata(df: pd.DataFrame):
    records = []

    for idx, row in df.iterrows():
        # ingredients 필드를 문자열 → 리스트로 변환
        try:
            ingredients = json.loads(row.get("ingredients", "[]"))
        except:
            ingredients = []

        records.append(
            {
                "faiss_index": int(idx),
                "id": int(row["id"]),
                "name_ko": row.get("name_ko", ""),
                "name_en": row.get("name_en", ""),
                "category": row.get("category", ""),
                "spicy_level": row.get("spicy_level", ""),
                "image_url": row.get("image_url", ""),
                "ingredients": ingredients,  # 리스트로 저장됨
                "description": row.get("description", ""),
            }
        )

    with open(METADATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"💾 Metadata saved → {METADATA_JSON_PATH}")


def main():
    print(f"📥 Loading CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)

    print("🧩 Building combined_text...")
    df["combined_text"] = df.apply(build_combined_text, axis=1)

    texts = df["combined_text"].tolist()

    print("✨ Creating embeddings...")
    embeddings = create_embeddings(texts)
    np.save(EMBEDDING_NPY_PATH, embeddings)
    print(f"💾 Saved embeddings → {EMBEDDING_NPY_PATH}")

    print("⚙️ Building FAISS index...")
    build_faiss_index(embeddings)

    print("🗂 Creating metadata JSON...")
    build_metadata(df)

    print("🎉 모든 작업 완료!")


if __name__ == "__main__":
    main()