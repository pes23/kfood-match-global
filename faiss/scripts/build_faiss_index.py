import os
import json
import numpy as np
import pandas as pd
import faiss

from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join("faiss", "data")

CSV_PATH = os.path.join(DATA_DIR, "kfood.csv")
EMBEDDING_NPY_PATH = os.path.join(DATA_DIR, "kfood_embeddings.npy")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "kfood_faiss.index")
METADATA_JSON_PATH = os.path.join(DATA_DIR, "kfood_metadata.json")

BATCH_SIZE = 64

# 🔥 무료 멀티링구얼 모델 (bge-m3)
MODEL_NAME = "BAAI/bge-m3"

def build_combined_text(row: pd.Series) -> str:
    """
    각 음식에 대해 임베딩에 사용할 텍스트 구성
    """
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


def create_embeddings(texts, model):
    """
    SentenceTransformer로 로컬 CPU 임베딩
    """
    print("🧠 Encoding with BGE model...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    print("📏 Embeddings shape:", embeddings.shape)
    return embeddings.astype("float32")


def build_faiss_index(embeddings: np.ndarray):
    """
    Inner Product 기반 FAISS Index 생성 (코사인 유사도)
    """
    d = embeddings.shape[1]

    faiss.normalize_L2(embeddings)  # 코사인 유사도용 정규화

    index = faiss.IndexFlatIP(d)
    index.add(embeddings)

    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"💾 Saved FAISS index → {FAISS_INDEX_PATH}")


def build_metadata(df: pd.DataFrame):
    """
    FastAPI에서 조회할 메타데이터 JSON 생성
    """
    records = []

    for idx, row in df.iterrows():
        records.append(
            {
                "faiss_index": int(idx),
                "id": int(row["id"]),
                "name_ko": row.get("name_ko", ""),
                "name_en": row.get("name_en", ""),
                "category": row.get("category", ""),
                "spicy_level": row.get("spicy_level", ""),
                "image_url": row.get("image_url", ""),
                "ingredients": row.get("ingredients", ""),
                "description": row.get("description", ""),
            }
        )
    with open(METADATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"💾 Metadata saved → {METADATA_JSON_PATH}")


def main():
    print(f"📥 Loading CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)

    print("🧩 Building combined_text for each row...")
    df["combined_text"] = df.apply(build_combined_text, axis=1)

    texts = df["combined_text"].tolist()

    print("🚀 Loading model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)

    print("✨ Creating embeddings...")
    embeddings = create_embeddings(texts, model)
    np.save(EMBEDDING_NPY_PATH, embeddings)
    print(f"💾 Saved embeddings → {EMBEDDING_NPY_PATH}")

    print("⚙️ Building FAISS index...")
    build_faiss_index(embeddings)

    print("🗂 Creating metadata JSON...")
    build_metadata(df)

    print("🎉 모든 작업 완료!")


if __name__ == "__main__":
    main()
