from typing import Optional, List

from pydantic import BaseModel

# id = Column(BigInteger, primary_key=True, index=True, unique=True)
# order = Column(SmallInteger)
# title = Column(String(128))
# description = Column(String)
# media_file_id = Column(String)
# media_type = Column(String(32))
# medias = relationship("Media", back_populates="practise", lazy="selectin")
# thumbs = Column(String, unique=True)


class Media(BaseModel):
    id: int
    is_free: bool = True
    free_content_file_id: Optional[str]
    comm_content_file_id: Optional[str]
    order: int
    media_type: str
    title: Optional[str]
    category: Optional[str]
    description: Optional[str]
    thumbs: Optional[str]
    cost: Optional[int]

    class Config:
        from_attributes = True


class PractiseBase(BaseModel):
    order: int
    title: Optional[str]
    description: Optional[str]
    media_file_id: Optional[str]
    media_type: Optional[str]
    thumbs: Optional[str]


class PractiseCreate(PractiseBase):
    pass


class PractiseUpdate(PractiseBase):
    id: int


class PractiseInDBBase(PractiseUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class PractiseInDB(PractiseInDBBase):
    pass


class Practise(PractiseInDBBase):
    medias: List[Media]
