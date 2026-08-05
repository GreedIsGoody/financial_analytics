from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class StatusSummary(BaseModel):
    status: str
    count: int
    total_amount: Decimal = Field(..., decimal_places=2, max_digits=18)


class AnalyticsSummaryResponse(BaseModel):
    total_transactions: int
    total_volume: Decimal = Field(..., decimal_places=2, max_digits=18)
    avg_transaction_amount: Decimal = Field(..., decimal_places=2, max_digits=18)
    by_status: list[StatusSummary]


class TopUserResponse(BaseModel):
    user_id: UUID
    total_spent: Decimal = Field(..., decimal_places=2, max_digits=18)
    transaction_count: int