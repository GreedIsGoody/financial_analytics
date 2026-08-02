from fastapi import FastAPI 
from app.core.config import settings 
from app.api.v1.transactions import router as transactions_router
from contextlib import asynccontextmanager
from app.core.clickhouse import init_clickhouse

@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_clickhouse()
    yield






app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

app.include_router(transactions_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status" : "ok"}