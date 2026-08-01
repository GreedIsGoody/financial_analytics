import uuid 
from decimal import Decimal 
from pydantic import BaseModel, Field 

class TransactionCreate(BaseModel):
    user_id: uuid.UUID
    amount: Decimal = Field(gt=0, description="Sum is need to be higher than 0")
    currency: str = Field(min_length=3, max_length=3, description="Code of currency, like USD etc.")
    
class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal 
    currency: str
    status: str
    
    class Config:
        from_attributes = True