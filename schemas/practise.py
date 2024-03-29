from typing import Optional, List
from pydantic import BaseModel
from schemas import MediaBase


class PractisePaidRequest(BaseModel):
    practise_id: int
    tg_id: int


class Media(BaseModel):
    id: int
    is_free: bool = True
    free_content_file_id: Optional[str]
    comm_content_file_id: Optional[str]
    order: int
    media_type: int
    title: Optional[str]
    category: Optional[str]
    description: Optional[str]
    cost: Optional[int]

    class Config:
        from_attributes = True


class PractiseBase(BaseModel):
    order: int
    title: Optional[str]
    description: Optional[str]
    media_file_id: Optional[str]
    media_type: Optional[int]
    is_published: bool = False
    file_resource_link: Optional[str] = None
    disk_resource_link: Optional[str] = None
    channel_resource_link: Optional[str] = None
    channel_web_link: Optional[str] = None
    channel_chat_id: Optional[int] = None
    poster: Optional[str] = None
    about: Optional[str] = None
    content: Optional[str] = None
    tag: Optional[str] = None
    cost: Optional[int] = None


class PractiseCreate(PractiseBase):
    category: int


class PractiseUpdate(PractiseBase):
    id: int
    category: Optional[int] = None


class PractiseInDBBase(PractiseUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class PractiseInDB(PractiseInDBBase):
    pass


class Practise(PractiseInDBBase):
    medias: List[MediaBase]
