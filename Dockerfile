# Stage 1: Build frontend
FROM node:22-slim AS frontend-build
WORKDIR /app
COPY crm/frontend/package.json crm/frontend/package-lock.json* ./
RUN npm install
COPY crm/frontend/ .
RUN npm run build

# Stage 2: Backend + static frontend
FROM python:3.11-slim
WORKDIR /app

COPY crm/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY crm/backend/ .

# Copy built frontend into backend static dir
COPY --from=frontend-build /app/dist /app/static

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
