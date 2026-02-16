from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.auth import router as auth_router

app = FastAPI(title="__PROJECT_NAME__ API")

app.include_router(auth_router, prefix="/api/auth")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# --- To enable MongoDB, uncomment the following: ---
# from app.routes.items import router as items_router
# app.include_router(items_router, prefix="/api")


# Serve built frontend in platform (single-container) mode.
# The `static/` directory is created by the Dockerfile `platform` target.
static_dir = Path(__file__).parent.parent / "static"
if static_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve the React SPA for any non-API route."""
        return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
