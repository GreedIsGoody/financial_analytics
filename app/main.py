import asyncio
from fastapi import FastAPI 
from app.core.config import settings 
from app.api.v1.transactions import router as transactions_router
from contextlib import asynccontextmanager
from app.core.clickhouse import init_clickhouse
from app.infrastructure.messaging.outbox_relayer import run_outbox_relayer

@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_clickhouse()
    
    relayer_task = asyncio.create_task(run_outbox_relayer(poll_interval=3))
    
    yield
    
    relayer_task.cancel()
    






app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

app.include_router(transactions_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status" : "ok"}