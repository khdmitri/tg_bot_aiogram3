from typing import Optional

from pydantic import BaseModel

from schemas.sphere import Sphere


class SphereUserBase(BaseModel):
    web_user_id: int
    order: int
    depth: int
    sphere_id: Optional[int]


# Properties to receive via API on creation
class SphereUserCreate(SphereUserBase):
    sphere_id: int


# Properties to receive via API on update
class SphereUserUpdate(SphereUserBase):
    id: int


class SphereUserInDBBase(SphereUserUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class SphereUserInDB(SphereUserInDBBase):
    pass


class SphereUser(SphereUserInDBBase):
    sphere: Sphere
