
# id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
# user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
# user = relationship("User", lazy="selectin")
# media_id = mapped_column(ForeignKey("media.id", ondelete='SET NULL'))
# media = relationship("Media", lazy="selectin")
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
