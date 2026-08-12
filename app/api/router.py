from fastapi import APIRouter
from app.api.routes import health, upload, embeddings, chat

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(embeddings.router)
api_router.include_router(chat.router)
