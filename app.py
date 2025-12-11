from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routes import router as api_router
from config import Config
from services.cache_service import CacheService


logger.add(
    Config.LOG_FILE,
    rotation="1 day",
    retention="7 days",
    level=Config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

app = FastAPI(title="SORMO Backend", version="1.0.0", debug=Config.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    CacheService().ensure_directories()
    logger.info("Backend iniciado")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host=Config.API_HOST, port=Config.API_PORT, reload=Config.DEBUG)
