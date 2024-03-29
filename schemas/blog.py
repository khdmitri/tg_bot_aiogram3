from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BlogBase(BaseModel):
    title: Optional[str]
    media_type: Optional[int]
    text: Optional[str]


# Properties to receive via API on creation
class BlogCreate(BlogBase):
    pass


# Properties to receive via API on update
class BlogUpdate(BlogBase):
    id: int
    media_path: Optional[str] = ""
    title: Optional[str] = None
    text: Optional[str] = None


class BlogInDBBase(BlogUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class BlogInDB(BlogInDBBase):
    create_date: datetime


class Blog(BlogInDBBase):
    pass
