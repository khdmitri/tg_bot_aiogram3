from typing import TYPE_CHECKING

from sqlalchemy import Column, String, SmallInteger, BigInteger, Boolean
from sqlalchemy.orm import relationship

from db.base_class import Base

if TYPE_CHECKING:
    from .media import Media # Noqa


class Practise(Base):
    id = Column(BigInteger, primary_key=True, index=True, unique=True)
    order = Column(SmallInteger)
    title = Column(String(128))
    description = Column(String)
    media_file_id = Column(String)
    media_type = Column(String(32))
    medias = relationship("Media", back_populates="practise", lazy="selectin", cascade="all, delete-orphan")
    thumbs = Column(String, unique=True)
    is_published = Column(Boolean, default=False)

    def as_dict(self):
        return {
            "id": self.id,
            "order": self.order,
            "title": self.title,
            "description": self.description,
            "media_type": self.media_type,
            "media_file_id": self.media_file_id,
            "thumbs": self.thumbs,
            "is_published": self.is_published,
        }
