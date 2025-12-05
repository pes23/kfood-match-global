// app/api/recommend/route.ts
import { NextRequest, NextResponse } from "next/server";
import type { RecommendationResponse } from "types/recommendation";

// K8s 내부용 + 로컬 개발용 둘 다 커버
const INTERNAL_URL =
  process.env.RECOMMENDER_INTERNAL_URL ??
  (process.env.NODE_ENV === "production"
    ? "http://kfood-recommender-service:80" // K8s 내부 서비스
    : "http://localhost:8010"); // 로컬: NodePort 또는 백엔드 포트

export async function POST(req: NextRequest) {
  try {
    const { foreignFood } = await req.json();

    // 입력값 검증
    if (!foreignFood || typeof foreignFood !== "string" || !foreignFood.trim()) {
      return NextResponse.json(
        { detail: "음식 이름을 입력해주세요." },
        { status: 400 }
      );
    }

    // 쿼리 파라미터로 넘김 (FastAPI가 Query(...)로 받으니까)
    const backendUrl = new URL("/recommend", INTERNAL_URL);
    backendUrl.searchParams.set("foreign_food", foreignFood.trim());

    const res = await fetch(backendUrl.toString(), {
      method: "POST",
    });

    // 백엔드에서 에러 반환한 경우
    if (!res.ok) {
      let detail = "추천 요청 중 오류가 발생했습니다.";
      try {
        const errJson = await res.json();
        if (errJson?.detail) detail = errJson.detail;
      } catch {
        // JSON 파싱 실패하면 기본 메시지 유지
      }

      return NextResponse.json({ detail }, { status: res.status });
    }

    const data = (await res.json()) as RecommendationResponse;
    return NextResponse.json(data);
  } catch (err) {
    console.error("Recommend proxy error:", err);
    return NextResponse.json(
      { detail: "서버 내부 오류가 발생했습니다." },
      { status: 500 }
    );
  }
}
