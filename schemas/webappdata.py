from typing import Optional

from pydantic import BaseModel, EmailStr


class WebAppData(BaseModel):
    action: int
    order_id: int
    user_id: int


class WebEmailData(BaseModel):
    action: int
    email: str


class WebCreatePaymentData(BaseModel):
    email: EmailStr
    practise_id: int


class UkassaPaymentSchema(BaseModel):
    payment_id: str
    confirmation_url: str


class UkassaEventSchema(BaseModel):
    id: str
    amount: int
    status: int


class SphereWebUser(BaseModel):
    id: int
    depth: int
    email: Optional[str]
