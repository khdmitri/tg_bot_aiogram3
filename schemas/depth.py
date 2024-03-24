from typing import Optional

from pydantic import BaseModel


class DepthBase(BaseModel):
    title: str
    duration: int
    best_time: Optional[str]
    description: Optional[str]


# Properties to receive via API on creation
class DepthCreate(DepthBase):
    pass


# Properties to receive via API on update
class DepthUpdate(DepthBase):
    id: int


class DepthInDBBase(DepthUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class DepthInDB(DepthInDBBase):
    pass


class Depth(DepthInDBBase):
    pass
