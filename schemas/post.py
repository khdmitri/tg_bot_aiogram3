from typing import Optional

from pydantic import BaseModel

# "id": self.id,
# "name": self.name,
# "order": self.order,
# "page": self.page,
# "message_type": self.message_type,
# "media_file_id": self.media_file_id,
# "text": self.text,


class PostBase(BaseModel):
    order: int
    name: Optional[str]
    page: Optional[str]
    media_file_id: Optional[str]
    message_type: Optional[int]
    text: Optional[str]
    media_group_id: Optional[int]


class PostCreate(PostBase):
    media_group_id: Optional[int] = None


class PostUpdate(PostBase):
    id: int
    media_group_id: Optional[int] = None


class PostInDBBase(PostUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class PostInDB(PostInDBBase):
    pass


class Post(PostInDBBase):
    pass
