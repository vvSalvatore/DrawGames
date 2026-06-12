# Multi-stage build for DrawGames frontend only

# Stage 1: Build frontend
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve built frontend statically
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/build ./build
RUN npm install -g serve
EXPOSE 3000
CMD ["sh", "-lc", "serve -s build -l ${PORT:-3000}"]
