# App Template

GitHub template repository for full-stack apps deployed on the platform. Use this as the starting point for every new application.

## Stack

- **Frontend**: React 19 + Vite 7, Tailwind CSS v4, shadcn/ui components, React Router
- **Backend**: FastAPI (Python 3.12), Uvicorn
- **Database**: MongoDB via Motor (opt-in)
- **Deployment**: Docker → GHCR → GitOps (FluxCD) → Kubernetes
- **CI/CD**: GitHub Actions (build on push to `main`, update gitops image tag)

---

## Quick Start

### 1. Create a new repo from this template

Click **"Use this template"** on GitHub → name your repo (e.g., `my-app`).

```bash
git clone https://github.com/makeiteasierapps/my-app.git
cd my-app
```

### 2. Initialize the project

```bash
./init.sh my-app
```

This replaces `__PROJECT_NAME__` across all files with your app name.

### 3. Local development

**Without Docker:**

```bash
# Frontend (terminal 1)
npm install
npm run dev          # → http://localhost:3000

# Backend (terminal 2)
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The Vite dev server proxies `/api` requests to the backend automatically.

**With Docker:**

```bash
docker compose up --build
```

- Frontend: http://localhost:3099 (nginx + Vite build)
- Backend: proxied at `/api` from the frontend container

---

## Deploying to the Platform

### One-time setup (per app)

1. **Add a `GITOPS_TOKEN` secret** to your GitHub repo (Settings → Secrets → Actions). Use a PAT with `repo` scope on the `makeiteasierapps/gitops` repo.
2. **Create the app in Observatory** (Deploy UI):
   - Generates Kubernetes manifests in the gitops repo (`apps/<app-name>/`)
   - Creates the AWS Secrets Manager secret for env vars (`apps/<app-name>/production`)
   - Creates the DNS record pointing to the cluster ingress

### Ongoing deploys

Push to `main` → GitHub Actions builds the `platform` Dockerfile target → pushes to GHCR → updates the image tag in the gitops repo → Flux deploys within ~1 minute.

---

## Project Structure

```
├── .github/workflows/
│   └── deploy.yml              # CI/CD: build + push GHCR + update gitops
├── client/
│   ├── App.jsx                 # Root React component
│   ├── index.css               # Tailwind v4 + shadcn theme
│   └── main.jsx                # React entry point with Router
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app + static file serving
│   │   ├── db.py               # MongoDB client (opt-in)
│   │   └── routes/
│   │       └── items.py        # Sample CRUD routes (opt-in)
│   ├── .env.example
│   └── requirements.txt
├── nginx/
│   └── nginx.conf              # Local dev: proxies /api to backend
├── .dockerignore
├── .gitignore
├── components.json             # shadcn/ui config
├── docker-compose.yml          # Local dev (frontend + backend + optional mongo)
├── Dockerfile                  # Multi-target: api, web, platform
├── eslint.config.js
├── index.html
├── init.sh                     # One-time placeholder replacement
├── jsconfig.json
├── package.json
├── vite.config.js
└── README.md
```

### Dockerfile targets

| Target | Purpose | Used by |
|--------|---------|---------|
| `web-builder` | Builds the Vite frontend | Internal stage |
| `api` | FastAPI backend only | `docker-compose` (local dev) |
| `web` | Nginx serving built frontend | `docker-compose` (local dev) |
| `platform` | Single container: FastAPI + built frontend | CI/CD → Kubernetes |

---

## MongoDB (Opt-in)

The template includes MongoDB support that's disabled by default.

### Enable MongoDB

1. **Uncomment** `motor>=3.3.0` in `server/requirements.txt`
2. **Uncomment** the MongoDB env vars in `server/.env.example` (and your `.env`)
3. **Uncomment** the router import in `server/app/main.py`:
   ```python
   from app.routes.items import router as items_router
   app.include_router(items_router, prefix="/api")
   ```

### Database connection modes

| Mode | `MONGO_URI_DEV` | When to use |
|------|-----------------|-------------|
| **Local MongoDB** | `mongodb://adminUser:password@localhost:27017/admin` | Isolated local dev (uncomment `mongodb` service in `docker-compose.yml`) |
| **VPN to cluster** | `mongodb://adminUser:password@10.50.10.10:27017/admin` | Dev machine connected to Headscale VPN — uses the cluster's MongoDB directly |
| **Production** | Set via AWS Secrets Manager → ExternalSecret | Automatic in Kubernetes |

Set `LOCAL_DEV=true` in your `.env` to use `MONGO_URI_DEV` instead of `MONGO_URI`.

---

## Environment Variables

App environment variables in production are managed via AWS Secrets Manager:

1. **Secret path**: `apps/<app-name>/production`
2. **Synced to Kubernetes** via `ExternalSecret` → creates a `<app-name>-env` Secret
3. **Injected into the pod** via `envFrom` in the Deployment manifest

You can manage env vars through the Observatory App Settings UI or directly in AWS Secrets Manager.

---

## Secrets Flow

```
AWS Secrets Manager (apps/<app>/production)
    ↓ ExternalSecret (refreshInterval: 1h)
Kubernetes Secret (<app>-env)
    ↓ envFrom
Pod environment variables
```
