from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InvoiceBase(BaseModel):
    uuid: str
    practise_id: int
    media_id: Optional[int] = None
    amount: int
    status: str
    user_id: int
    is_full_practise: bool = False


class InvoiceCreate(InvoiceBase):
    valid_to: Optional[datetime] = None
    ticket_count: int = 1
    category: int


class InvoiceUpdate(InvoiceBase):
    id: int


class InvoiceInDBBase(InvoiceUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class InvoiceInDB(InvoiceInDBBase):
    pass


class Invoice(InvoiceInDBBase):
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    ticket_count: int
