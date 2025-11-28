# --- 1) Build Stage ---
FROM node:18-alpine AS builder

WORKDIR /app

# 패키지 파일 먼저 복사 → 캐시 최적화
COPY package.json package-lock.json ./

# 의존성 설치
RUN npm install

# 소스 코드 전체 복사
COPY . .

# Next.js 프로덕션 빌드
RUN npm run build


# --- 2) Production Run Stage ---
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

# Next.js는 standalone 모드로 런타임에 필요한 파일만 카피
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# 기본 포트
EXPOSE 3000

# Next.js 실행
CMD ["node", "server.js"]
