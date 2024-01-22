from typing import Optional

from pydantic import BaseModel

# "id": self.id,
# "name": self.name,
# "order": self.order,
# "page": self.page,
# "message_type": self.message_type,
# "media_file_id": self.media_file_id,
# "text": self.text,


class MediaGroupBase(BaseModel):
    media_type: Optional[int]
    media_group_id: Optional[int]
    media_file_id: Optional[str]


class MediaGroupCreate(MediaGroupBase):
    pass


class MediaGroupUpdate(MediaGroupBase):
    id: int


class MediaGroupInDBBase(MediaGroupUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class MediaGroupInDB(MediaGroupInDBBase):
    pass


class MediaGroup(MediaGroupInDBBase):
    pass
