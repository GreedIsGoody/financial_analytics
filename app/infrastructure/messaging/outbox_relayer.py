import asyncio
import logging 
from sqlalchemy import select, update 
from app.core.postgres import async_session_maker
from app.infrastructure.db.models import OutboxEventModel
from app.core.clickhouse import get_clickhouse_client

async def process_outbox_events():
    async with async_session_maker() as session:
        #Events with status PENDING
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.status == "PENDING")
            .limit(100)
        )
        result = await session.execute(stmt)
        events = result.scalars().all()
        
        if not events:
            return 
        print(f"🚚 found {len(events)} events what was not sent.")
        
        #Format batch for Clickhouse
        ch_rows = []
        processed_ids = []
        
        for event in events:
            p = event.payload
            ch_rows.append(
                (
                    p["transaction_id"],
                    p["user_id"],
                    p["amount"],
                    p["currency"],
                    p["status"],
                    p["created_at"],
                )
            )
            processed_ids.append(event.id)
            
            
        async with await get_clickhouse_client() as ch_client:
            await ch_client.insert(
                table="transaction_analytics",
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
            .values(status="PROCESSED")
        )
        await session.execute(update_stmt)
        await session.commit()
        
        print(
            f"✅ {len(events)} events succesfully sended to ClickHouse!"
        )
        
async def run_outbox_relayer(poll_interval: int = 3):
    print("Outbox relayer is working")
    while True:
        try:
            await process_outbox_events()
        except Exception as e:
            print("Outbox layer error : {e}")
        await asyncio.sleep(poll_interval)