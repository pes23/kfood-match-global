import type { RecommendationResponse } from "@/types/recommendation";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchRecommendations(
  foreignFood: string
): Promise<RecommendationResponse> {
  if (!foreignFood.trim()) {
    throw new Error("음식 이름을 입력해주세요.");
  }

  const url = `${BASE_URL}/recommend?foreign_food=${encodeURIComponent(
    foreignFood
  )}`;

  const res = await fetch(url, {
    method: "POST",
  });

  if (!res.ok) {
    const message = await res
      .json()
      .catch(() => ({ detail: "Unknown error" }));
    throw new Error(message.detail ?? "추천 요청 중 오류가 발생했습니다.");
  }

  const data = (await res.json()) as RecommendationResponse;
  return data;
}
