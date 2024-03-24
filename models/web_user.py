from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base_class import Base


class WebUser(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    sphere_update: Mapped[datetime] = mapped_column(DateTime, nullable=True)
