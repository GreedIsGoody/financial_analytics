from decimal import Decimal 
from uuid import UUID  
from clickhouse_connect.driver.asyncclient import AsyncClient 
import math
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
            FROM transactions_analytics
        """
        
        total_res = await self.ch_client.query(total_query)
        
        total_cnt = 0
        total_vol = Decimal("0")
        avg_amt = Decimal("0")
        
        if total_res.result_rows and total_res.result_rows[0]:
            cnt, vol, avg_val = total_res.result_rows[0]
            total_cnt = int(cnt or 0)
            
            TWO_PLACES = Decimal("0.01")
            
            if vol is not None and not (isinstance(vol, float) and math.isnan(vol)):
                total_vol = Decimal(str(vol)).quantize(TWO_PLACES)

            if avg_val is not None and not (
                isinstance(avg_val, float) and math.isnan(avg_val)
            ):
                avg_amt = Decimal(str(avg_val)).quantize(TWO_PLACES)
        #Counting agregate by status 
        status_query = """
            SELECT
                status,
                count() as cnt,
                sum(amount) as vol
            FROM transactions_analytics
            GROUP BY status
        """
        status_res = await self.ch_client.query(status_query)
        
        by_status = []
        if status_res.result_rows:
            for row in status_res.result_rows:
                status_name = str(row[0])
                status_cnt = int(row[1] or 0)
                status_vol = Decimal("0")

                if row[2] is not None and not (
                    isinstance(row[2], float) and math.isnan(row[2])
                ):
                    status_vol = Decimal(str(row[2])).quantize(TWO_PLACES)

                by_status.append(
                    StatusSummary(
                        status=status_name,
                        count=status_cnt,
                        total_amount=status_vol,
                    )
                )

        return AnalyticsSummaryResponse(
            total_transactions=total_cnt,
            total_volume=total_vol,
            avg_transaction_amount=avg_amt,
            by_status=by_status,
        )
    async def get_top_users(
        self, limit: int = 10, days: int = 30
    ) -> list[TopUserResponse]:
        query = """
            SELECT 
                user_id,
                sum(amount) as total_spent,
                count() as tx_count
            FROM transactions_analytics
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