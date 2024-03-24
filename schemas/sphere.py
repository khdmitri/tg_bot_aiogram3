from typing import Optional

from pydantic import BaseModel


class SphereBase(BaseModel):
    title: str
    duration: int
    best_time: Optional[str]
    description: Optional[str]


# Properties to receive via API on creation
class SphereCreate(SphereBase):
    pass


# Properties to receive via API on update
class SphereUpdate(SphereBase):
    id: int


class SphereInDBBase(SphereUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class SphereInDB(SphereInDBBase):
    pass


class Sphere(SphereInDBBase):
    pass
