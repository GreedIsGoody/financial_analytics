import clickhouse_connect 
from clickhouse_connect.driver.asyncclient import AsyncClient
from app.core.config import settings 


async def get_clickhouse_client() -> AsyncClient:
    return await clickhouse_connect.get_async_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_DB,
    )
    
async def init_clickhouse():
    client = await get_clickhouse_client()
    #async with to automatically close aihttp-session
    async with client:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transactions_analytics (
            id UUID,
            user_id UUID,
            amount Decimal(18, 4),
            currency LowCardinality(String),
            status LowCardinality(String),
            created_at DateTime
        )
        ENGINE = MergeTree()
        ORDER BY (created_at, user_id);
        """
        await client.command(create_table_query)
        print("✅ Clickhouse table 'transaction_analytics' ready!")
    