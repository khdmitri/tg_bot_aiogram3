from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserPaymentBase(BaseModel):
    paid_amount: int
    user_id: int
    media_id: Optional[int]
    practise_id: Optional[int]
    invoice_id: int


# Properties to receive via API on creation
class UserPaymentCreate(UserPaymentBase):
    pass


# Properties to receive via API on update
class UserPaymentUpdate(UserPaymentBase):
    id: int


class UserPaymentInDBBase(UserPaymentUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class UserPaymentInDB(UserPaymentInDBBase):
    pass


class UserPayment(UserPaymentInDBBase):
    create_date: datetime
    update_date: datetime
