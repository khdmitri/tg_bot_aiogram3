from sqlalchemy import Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.base_class import Base
from utils.constants import MessageTypes


class MediaGroup(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    media_type: Mapped[int] = mapped_column(Integer, default=MessageTypes.NOT_DEFINED)
    media_file_id: Mapped[str] = mapped_column(String)
    media_group_id: Mapped[int] = mapped_column(BigInteger)

    def as_dict(self):
        return {
            "id": self.id,
            "media_type": self.media_type,
            "media_file_id": self.media_file_id,
            "media_group_id": self.media_group_id,
        }
