from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.database import get_db
from app.lifespan import lifespan
from app.api.users import router as users_router
from app.api.resources import router as resources_router
from app.api.telegram import router as telegram_router
from app.api.monitoring import router as monitoring_router

# Используем lifespan вместо on_event
app = FastAPI(
    title="Telegram Notifier API",
    description="Enterprise backend for telegram notifications",
    version="0.1.0",
    lifespan=lifespan  # ← ПЕРЕДАЕМ LIFESPAN
)

# Include routers
app.include_router(users_router)
app.include_router(resources_router)
app.include_router(telegram_router)
app.include_router(monitoring_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint with database connection test."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.app_env,
        "debug": settings.debug
    }

@app.get("/")
async def root():
    return {"message": "Welcome to Telegram Notifier API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )