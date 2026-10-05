from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.chat import router as chat_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI powered production operations agent."
)

app.include_router(chat_router)

@app.get("/")
async def root():
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "message": "OpsPilot API is running!"
    }
    
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": settings.environment
    }