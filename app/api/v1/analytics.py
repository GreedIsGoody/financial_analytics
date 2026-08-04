from fastapi import APIRouter, Depends, Query   
from clickhouse_connect.driver.asyncclient import AsyncClient  

from app.core.clickhouse import get_clickhouse_client
from app.infrastructure.analytics_repository import AnalyticsRepository
from app.domain.analytics import AnalyticsSummaryResponse, TopUserResponse


router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    ch_client: AsyncClient = Depends(get_clickhouse_client),
):
    """
    Get aggregated transactional analytics from ClickHouse.
    """
    repo = AnalyticsRepository(ch_client)
    return await repo.get_summary()


@router.get("/top-users", response_model=list[TopUserResponse])
async def get_top_users(
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(30, ge=1, le=365),
    ch_client: AsyncClient = Depends(get_clickhouse_client),
):
    """
    Get top users by spending volume over the last N days.
    """
    repo = AnalyticsRepository(ch_client)
    return await repo.get_top_users(limit=limit, days=days)