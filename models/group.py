from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, DateTime, Boolean, func, SmallInteger, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.base_class import Base

if TYPE_CHECKING:
    from .media import Media # Noqa
    from .user import User # Noqa


class Group(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user = relationship("User", lazy="selectin")
    media_id = mapped_column(ForeignKey("media.id", ondelete='SET NULL'))
    media = relationship("Media", lazy="selectin")
