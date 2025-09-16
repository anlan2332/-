# BaiKaoTong AI Writing Platform - Multi-stage Dockerfile
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Backend Runtime
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for PM2
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install PM2 globally
RUN npm install -g pm2

# Create app directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy built frontend from first stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Copy deployment configurations
COPY deployment/config/ ./config/
COPY deployment/scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p logs uploads data

# Set permissions
RUN chmod +x scripts/*.sh

# Expose ports
EXPOSE 5000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start command
CMD ["./scripts/start-production.sh"]