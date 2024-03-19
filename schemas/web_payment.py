from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from models.base import BaseModel
from schemas import WebUser
from schemas.practise import PractiseBase


class WebPaymentBase(BaseModel):
    web_user_id: int
    practise_id: int
    amount: Optional[int] = 0


class WebPaymentCreate(WebPaymentBase):
    payment_id: int


class WebPaymentUpdate(WebPaymentBase):
    payment_id: int


class WebPaymentInDBBase(WebPaymentUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class WebPaymentInDB(WebPaymentInDBBase):
    create_date: datetime
    update_date: datetime


class WebPayment(WebPaymentInDBBase):
    web_user: WebUser
    practise: PractiseBase
