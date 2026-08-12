import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.security import setup_cors
from app.core.logger import logger
from app.api.router import api_router
from app.api.dependencies import get_rag_service
from app.services.sync.uploads_watcher import UploadsWatcher

uploads_watcher: UploadsWatcher | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global uploads_watcher
    logger.info(f"Starting {settings.APP_NAME} in [{settings.ENVIRONMENT}] mode.")

    uploads_dir = settings.BASE_DIR / settings.UPLOADS_DIR
    uploads_watcher = UploadsWatcher(rag_service=get_rag_service(), uploads_dir=uploads_dir)
    uploads_watcher.start()

    yield

    if uploads_watcher:
        uploads_watcher.stop()
    logger.info(f"Shutting down {settings.APP_NAME}.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Retrieval-Augmented Generation (RAG) System API",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup CORS Middleware
setup_cors(app)

# Include API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Static Files & Web UI Dashboard
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", include_in_schema=False)
async def serve_ui():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": f"Welcome to {settings.APP_NAME} API. Visit /docs for Swagger UI."}


if __name__ == "__main__":
    import uvicorn
    # Exclude data/logs/storage from the --reload watcher: those folders
    # change constantly (uploads, vector DB files, log writes) and are not
    # code. Without this, dropping/removing a document restarts the whole
    # server (reloads the embedding model, wipes in-memory chat sessions)
    # instead of being picked up quietly by UploadsWatcher.
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=[
            "data/*",
            "logs/*",
            "app/storage/*",
        ],
    )
