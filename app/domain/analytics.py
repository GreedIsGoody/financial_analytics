from decimal import Decimal 
from pydantic import BaseModel 
from uuid import UUID 

class StatusSummary(BaseModel):
    status: str
    count: int 
    total_amount: Decimal 
    
class AnalyticsSummaryResponse(BaseModel):
    total_transactions: int 
    total_volume: Decimal 
    avg_transaction_amount : Decimal
    by_status: list[StatusSummary]
    
class TopUserResponse(BaseModel):
    user_id: UUID
    total_spent: Decimal 
    transaction_count: int