from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserByTgId(BaseModel):
    tg_id: int


class UserPayment(BaseModel):
    paid_amount: int
    user_id: int
    media_id: Optional[int]
    practise_id: Optional[int]
    invoice_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: Optional[str] = None
    fullname: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    tg_id: int
    last_visit: datetime
    email: Optional[EmailStr] = None
    contact: Optional[str] = None


# Properties to receive via API on update
class UserUpdate(UserBase):
    id: int
    last_visit: datetime


class UserInDBBase(UserUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    pass


class User(UserInDBBase):
    create_date: datetime
    update_date: datetime
    payments: List[UserPayment]
