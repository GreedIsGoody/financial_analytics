from fastapi import APIRouter, Depends, status 
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgres import get_async_session 
from app.domain.models import TransactionCreate, TransactionResponse
from app.infrastructure.db.models import TransactionModel, OutboxEventModel

router = APIRouter(prefix="/transaction", tags=["Transactions"])

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    session: AsyncSession = Depends(get_async_session)
):
    #Creating transaction with absolute dependability
    async with session.begin():
        
        #Creating transaction
        new_transaction = TransactionModel(
            user_id = payload.user_id,
            amount = payload.amount,
            currency= payload.currency,
            status="PAID"
        )
        session.add(new_transaction) 
        await session.flush() #Receing a generated UUID for new_transaction.id
        
        #Event to our broker
        event_payload = {
            "transaction_id": str(new_transaction.id),
            "user_id": str(new_transaction.user_id),
            "amount": float(new_transaction.amount),
            "currency": new_transaction.currency,
            "status": new_transaction.status,
            "created_at": new_transaction.created_at.isoformat() if new_transaction.created_at else None
        }
        outbox_event = OutboxEventModel(
            aggregate_type="transaction",
            aggregate_id = str(new_transaction.id),
            event_type="TransactionCreated",
            payload=event_payload
        )
        session.add(outbox_event)
        
    return new_transaction
        
        