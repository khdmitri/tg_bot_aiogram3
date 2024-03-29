from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db.base_class import Base


class Blog(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    title: Mapped[str] = mapped_column(String, nullable=True)
    media_type: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(String, nullable=True)
    media_path: Mapped[str] = mapped_column(String, nullable=True)
