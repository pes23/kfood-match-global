// lib/api.ts
import type { RecommendationResponse } from "types/recommendation";

export async function fetchRecommendations(
  foreignFood: string
): Promise<RecommendationResponse> {
  if (!foreignFood.trim()) {
    throw new Error("음식 이름을 입력해주세요.");
  }

  const res = await fetch("/api/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ foreignFood }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "추천 요청 중 오류가 발생했습니다.");
  }

  return res.json();
}
