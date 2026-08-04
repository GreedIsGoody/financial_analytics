from decimal import Decimal 
from uuid import UUID  
from clickhouse_connect.driver.asyncclient import AsyncClient 

from app.domain.analytics import (
    AnalyticsSummaryResponse,
    StatusSummary,
    TopUserResponse,
)


class AnalyticsRepository:
    
    def __init__(self, ch_client:AsyncClient):
        self.ch_client = ch_client
        
        
    async def get_summary(self) -> AnalyticsSummaryResponse:
        #Total statistics 
        
        total_query = """
            SELECT
                count() as total_cnt,
                sum(amount) as total_vol,
                avg(amount) as avg_amt
            FROM default.transactions_analytics
        """
        
        total_res = await self.ch_client.query(total_query)
        total_cnt, total_vol, avg_amt = total_res.first_row
        
        #Counting agregate by status 
        status_query = """
            SELECT
                status,
                count() as cnt,
                sum(amount) as vol
            FROM default.transactions_analytics
            GROUP BY status
        """
        status_res = await self.ch_client.query(status_query)
        
        by_status = [
            StatusSummary(
                status=row[0],
                count=row[1],
                total_amount=Decimal(str(row[2] or 0))
            )
            for row in status_res.result_row
        ]
        return AnalyticsSummaryResponse(
            total_transactions=total_cnt or 0,
            total_volume = Decimal(str(total_vol or 0)),
            avg_transaction_amount = Decimal(str(avg_amt or 0)),
            by_status=by_status
            )
    async def get_top_users(
        self, limit: int = 10, days: int = 30
    ) -> list[TopUserResponse]:
        query = """
            SELECT 
                user_id,
                sum(amount) as total_spent,
                count() as tx_count
            FROM default.transactions_analytics
            WHERE created_at >= now() - INTERVAL %s DAY
            GROUP BY user_id
            ORDER BY total_spent DESC
            LIMIT %s
        """
        res = await self.ch_client.query(query, parameters=(days, limit))

        return [
            TopUserResponse(
                user_id=UUID(row[0]) if isinstance(row[0], str) else row[0],
                total_spent=Decimal(str(row[1])),
                transaction_count=row[2],
            )
            for row in res.result_rows
        ]