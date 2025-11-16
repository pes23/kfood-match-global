# faiss/scripts/merge_kfood_data.py

import pandas as pd
import os

DATA_DIR = "faiss/data"
HANSIK_PATH = os.path.join(DATA_DIR, "hansik_guide_raw.xlsx")
OUTPUT_CSV = os.path.join(DATA_DIR, "kfood.csv")


def normalize(name: str) -> str:
    """음식명 정규화"""
    if pd.isna(name):
        return ""
    name = str(name).strip()
    if "(" in name:
        name = name.split("(")[0]
    return name.lower()


def main():
    print("📥 Loading Hansik Excel...")

    # ✔ header=2 : 실제 컬럼명이 3번째 줄(row index=2)에 있음
    df = pd.read_excel(HANSIK_PATH, header=2)

    print("📑 Detected columns:", df.columns.tolist())

    # ✔ A열은 비어 있으므로 drop
    if df.columns[0] != "요리번호":
        df = df.drop(df.columns[0], axis=1)

    # ✔ 필요한 컬럼 추출 (너가 말한 순서 그대로)
    df_small = df[
        ["요리번호", "800선 카테고리", "요리명", "라틴어 발음",
         "설명(요리명제외)", "영어", "설명(요리명제외).1"]
    ].copy()

    df_small = df_small.rename(columns={
        "요리명": "name_ko",
        "영어": "name_en",
        "설명(요리명제외)": "description_ko",
        "설명(요리명제외).1": "description_en",
        "800선 카테고리": "category"
    })

    # ✔ description: 영어 설명 > 한국어 설명
    df_small["description"] = df_small.apply(
        lambda r: r["description_en"] if pd.notna(r["description_en"]) else r["description_ko"],
        axis=1
    )

    df_small["name_key"] = df_small["name_ko"].apply(normalize)

    # ✔ name_ko가 비어있는 경우 제거
    df_small = df_small[df_small["name_ko"].notna()]

    # ✔ 최종 CSV 구조 만들기
    df_out = pd.DataFrame({
        "id": range(1, len(df_small) + 1),
        "name_ko": df_small["name_ko"],
        "name_en": df_small["name_en"],
        "description": df_small["description"],
        "ingredients": "",
        "category": df_small["category"],
        "spicy_level": "",
        "image_url": ""
    })

    df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ kfood.csv 생성 완료 → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
