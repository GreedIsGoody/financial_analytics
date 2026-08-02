from typing import AsyncGenerator 
from sqlalchemy.ext.asyncio  import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings  

#Async engine
engine = create_async_engine(
    settings.DATABASE_URL_ASYNCPG,
    echo=True,
    pool_size=10,
    max_overflow=20,
)
#Fabrif of async sessions
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

#FastAPI dependency injection
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session 