from datetime import datetime

from pydantic import EmailStr

from models.base import BaseModel


class WebUserBase(BaseModel):
    email: EmailStr


class WebUserCreate(WebUserBase):
    pass


class WebUserUpdate(WebUserBase):
    id: int


class WebUserInDBBase(WebUserUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class WebUserInDB(WebUserInDBBase):
    pass


class WebUser(WebUserInDBBase):
    create_date: datetime
