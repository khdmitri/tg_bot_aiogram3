from models.base import BaseModel


class GroupBase(BaseModel):
    user_id: int
    media_id: int


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    id: int


class GroupInDBBase(GroupUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class GroupInDB(GroupInDBBase):
    pass


class Group(GroupInDBBase):
    pass
