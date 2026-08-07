import asyncio
import json
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
 
from app.core.websockets import manager, ws_router
from app.core.config import settings 
from app.api.v1.transactions import router as transactions_router
from app.core.clickhouse import init_clickhouse
from app.infrastructure.messaging.outbox_relayer import run_outbox_relayer
from app.api.v1.analytics import router as analytics_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

async def redis_listener():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        protocol=2
    )
    pubsub= redis.pubsub()
    await pubsub.subscribe("analytics_events")
    logger.info("📡 Succesfull subscribe to  Redis channal: analytics_events")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                raw_data = message["data"]
                if isinstance(raw_data, bytes):
                    raw_data = raw_data.decode("utf-8")
                data = json.loads(raw_data)
                
                logger.info(f"📩 Sending event to WebSockets: {data}")
                await manager.broadcast(data)
            
    except asyncio.CancelledError:
        await pubsub.unsubscribe("analytics_events")
        await redis.close()
        logger.info("Subscribe on Redis is closed")


@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_clickhouse()
    
    relayer_task = asyncio.create_task(run_outbox_relayer(poll_interval=3))
    redis_task = asyncio.create_task(redis_listener())
    
    yield
    
    relayer_task.cancel()
    redis_task.cancel()
    
    for task in (relayer_task, redis_task):
        try:
            await task
        except asyncio.CancelledError:
            pass    






app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

app.include_router(transactions_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status" : "ok"}