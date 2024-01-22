from sqlalchemy import String, Integer, JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.base_class import Base


class Post(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    page: Mapped[str] = mapped_column(String)
    media_file_id: Mapped[str] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(String, nullable=True)
    message_type: Mapped[int] = mapped_column(Integer, default=0)
    order: Mapped[int] = mapped_column(Integer, default=0)
    media_group_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "page": self.page,
            "message_type": self.message_type,
            "media_file_id": self.media_file_id,
            "text": self.text,
            "media_group_id": self.media_group_id,
        }
