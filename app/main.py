from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db, wait_for_db
from app.api.users import router as users_router
from app.api.resources import router as resources_router

app = FastAPI(
    title="Telegram Notifier API",
    description="Enterprise backend for telegram notifications",
    version="0.1.0"
)

# Include routers
app.include_router(users_router)
app.include_router(resources_router)

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
    # Проверяем что приложение работает и БД доступна
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.app_env
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