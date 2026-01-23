# SmartSortierer Pro - Frontend with Angular Dashboard
# Multi-stage build: Node for Angular build, nginx for serving

# Stage 1: Build Angular app
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY smartsortierer-ui/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY smartsortierer-ui/ ./

# Build Angular app
RUN npm run build

# Stage 2: Nginx server
FROM nginx:alpine

# Copy built Angular app from builder stage
COPY --from=builder /app/dist/smartsortierer-ui/browser /usr/share/nginx/html

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1
