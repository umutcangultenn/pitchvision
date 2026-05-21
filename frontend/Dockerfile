# syntax=docker/dockerfile:1

# ── Base: bağımlılıkları yükle ────────────────────────────────────────────────
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline

# ── Development ───────────────────────────────────────────────────────────────
FROM base AS development
# node_modules base'den gelir; kaynak kod volume ile mount edilir
EXPOSE 3000
ENV NODE_ENV=development
CMD ["npm", "run", "dev"]

# ── Builder ───────────────────────────────────────────────────────────────────
FROM base AS builder
COPY . .
ENV NODE_ENV=production
RUN npm run build

# ── Production ────────────────────────────────────────────────────────────────
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
