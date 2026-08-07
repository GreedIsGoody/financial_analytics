import asyncio
import logging
import json
import redis.asyncio as aioredis
from datetime import datetime, timezone
from sqlalchemy import select, update 
from app.core.postgres import async_session_maker
from app.infrastructure.db.models import OutboxEventModel
from app.core.clickhouse import get_clickhouse_client
from app.core.config import settings 


redis_client = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    protocol=2
)

logger = logging.getLogger(__name__)


async def close_redis_client() -> None:
    await redis_client.aclose()

async def process_outbox_events():
    async with async_session_maker() as session:
        #Events with status PENDING
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.processed == False)
            .limit(100)
        )
        result = await session.execute(stmt)
        events = result.scalars().all()
        
        if not events:
            return 
        logger.info(f"🚚 found {len(events)} events what was not sent.")
        
        
        
        #Format batch for Clickhouse
        ch_rows = []
        processed_ids = []
        ws_payloads = []
        
        for event in events:
            p = event.payload
            
            raw_created_at = p.get("created_at")
            if isinstance(raw_created_at, str):
                created_at_dt = datetime.fromisoformat(raw_created_at)
            elif isinstance(raw_created_at, datetime):
                created_at_dt = raw_created_at
            else:
                created_at_dt = datetime.now(timezone.utc)
            
            if created_at_dt.tzinfo is not None:
                created_at_dt = created_at_dt.replace(tzinfo=None)
            
            
            ch_rows.append(
                (
                    p["transaction_id"],
                    p["user_id"],
                    p["amount"],
                    p["currency"],
                    p["status"],
                    created_at_dt,
                )
            )
            processed_ids.append(event.id)
            
            #Publicate a event in Redis PUB for WEBSOCKETS
            ws_payloads.append({
                "event_type": event.event_type,
                "data" : {
                    "transaction_id":  str(p["transaction_id"]),
                    "user_id": str(p["user_id"]),
                    "amount": str(p["amount"]),
                    "currency": p["currency"],
                    "status": p["status"],
                    "created_at": created_at_dt.isoformat(),
                },
            })
            
            
            
        async with await get_clickhouse_client() as ch_client:
            await ch_client.insert(
                table="transactions_analytics",
                column_names = [
                    "id",
                    "user_id",
                    "amount",
                    "currency",
                    "status",
                    "created_at"
                ],
                data=ch_rows,
            )
        update_stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id.in_(processed_ids))
            .values(processed=True)
        )
        await session.execute(update_stmt)
        await session.commit()
        
        logger.info(
            f"✅ {len(events)} events succesfully sended to ClickHouse!"
        )
        for payload in ws_payloads:
            await redis_client.publish("analytics_events", json.dumps(payload))
        
            
        
        
        
async def run_outbox_relayer(poll_interval: int = 3):
    
    logger.info("Outbox Relayer running.")
    backoff = poll_interval
    
    while True:
        try:
            await process_outbox_events()
            backoff=poll_interval
            
        except asyncio.CancelledError:
            logger.info("🛑 Outbox Relayer (Graceful Shutwodn)...")
            break
        
        except Exception as e:
            logger.error(f"Outbox layer error : {e}. Retry after {backoff} sec")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
            continue
        
        await asyncio.sleep(poll_interval)
