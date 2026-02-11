# === Stage 1: Build frontend ===
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies first (layer caching)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build


# === Stage 2: Serve with nginx ===
FROM nginx:1.27-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built frontend
COPY --from=builder /app/dist /usr/share/nginx/html

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-check-certificate -qO /dev/null https://localhost/ || wget -qO /dev/null http://localhost/ || exit 1

EXPOSE 80
EXPOSE 443
