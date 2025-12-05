# --- 1) BUILD ---
FROM node:18-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build


# --- 2) RUN ---
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# standalone server 전체 복사
COPY --from=builder /app/.next/standalone ./ 
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

# ▶ 반드시 standalone server.js 경로를 실행해야 한다
CMD ["node", "server.js", "-H", "0.0.0.0", "-p", "3000"]
