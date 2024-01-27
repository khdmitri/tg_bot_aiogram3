from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# id = Column(BigInteger, primary_key=True, index=True, unique=True)
# is_free = Column(Boolean, default=True)
# free_content_file_id = Column(String, index=True, unique=True)
# comm_content_file_id = Column(String, index=True, unique=True)
# order = Column(SmallInteger)
# media_type = Column(String(64))
# title = Column(String)
# category = Column(String(32))
# description = Column(String)
# thumbs = Column(String, unique=True)
# cost = Column(BigInteger)
# create_date = Column(DateTime, server_default=func.now())
# update_date = Column(DateTime, onupdate=func.now())
# practise_id: Mapped[int] = mapped_column(ForeignKey("practise.id"))
# practise = relationship("Practise", back_populates="medias", lazy="selectin")

class Practise(BaseModel):
    id: int
    order: int
    title: Optional[str]
    description: Optional[str]
    media_file_id: Optional[str]
    media_type: Optional[int]
    thumbs: Optional[str]

    class Config:
        from_attributes = True


class MediaBase(BaseModel):
    is_free: bool = True
    free_content_file_id: Optional[str]
    comm_content_file_id: Optional[str]
    order: int
    media_type: Optional[int]
    title: Optional[str]
    category: Optional[str]
    description: Optional[str]
    cost: Optional[int]
    media_group_id: Optional[int]


class MediaCreate(MediaBase):
    practise_id: int
    media_group_id: Optional[int] = None
    action_date: Optional[datetime] = None


class MediaUpdate(MediaBase):
    id: int
    media_group_id: Optional[int] = None
    stream_link: Optional[str] = None
    action_date: Optional[datetime] = None


class MediaInDBBase(MediaUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class MediaInDB(MediaInDBBase):
    pass


class Media(MediaInDBBase):
    create_date: datetime
    update_date: datetime
    practise: Practise
