from typing import TYPE_CHECKING

from sqlalchemy import Column, String, DateTime, Boolean, func, SmallInteger, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.base_class import Base

if TYPE_CHECKING:
    from .practise import Practise # Noqa


class Media(Base):
    id = Column(BigInteger, primary_key=True, index=True, unique=True)
    is_free = Column(Boolean, default=True)
    free_content_file_id = Column(String, index=True, unique=True)
    comm_content_file_id = Column(String, index=True, unique=True)
    order = Column(SmallInteger)
    media_type: Mapped[int] = mapped_column(Integer, default=0)
    title = Column(String)
    category = Column(String(32))
    description = Column(String)
    thumbs = Column(String, unique=True)
    cost = Column(BigInteger)
    create_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, onupdate=func.now())
    practise_id: Mapped[int] = mapped_column(ForeignKey("practise.id"))
    practise = relationship("Practise", back_populates="medias", lazy="selectin")
    media_group_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "is_free": self.is_free,
            "order": self.order,
            "title": self.title,
            "description": self.description,
            "media_type": self.media_type,
            "free_content_file_id": self.free_content_file_id,
            "comm_content_file_id": self.comm_content_file_id,
            "category": self.category,
            "cost": self.cost,
            "practise": self.practise.title,
            "practise_id": self.practise_id,
            "media_group_id": self.media_group_id,
        }
