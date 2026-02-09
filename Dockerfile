# -------- Web build stage --------
FROM node:__NODE_VERSION__-alpine AS web-builder

WORKDIR /app

# Install deps and build
COPY package.json ./
RUN npm install --prefer-offline --no-audit
COPY . .

# Build the app
RUN npm run build

# -------- API image (FastAPI/Uvicorn) --------
FROM python:__PYTHON_VERSION__-slim AS api

WORKDIR /app
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY server/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# -------- Web image (Nginx serving Vite build) --------
FROM nginx:alpine AS web

# Copy built frontend into Nginx default html dir
COPY --from=web-builder /app/dist /usr/share/nginx/html

# Nginx config (expects to listen on 3099 and proxy /api to the 'backend' service)
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3099

# -------- Platform image (single container for k8s) --------
FROM python:__PYTHON_VERSION__-slim AS platform

WORKDIR /app
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY server/app ./app

# Built frontend
COPY --from=web-builder /app/dist ./static

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
