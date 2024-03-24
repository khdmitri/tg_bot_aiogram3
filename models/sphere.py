from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base

if TYPE_CHECKING:
    from .web_user import WebUser # Noqa


class Depth(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    title: Mapped[str] = mapped_column(String)
    duration: Mapped[int] = mapped_column(Integer, default=30)
    best_time: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    def as_dict(self):
        return {
            "title": self.title,
            "duration": self.duration,
            "best_time": self.best_time,
            "description": self.description
        }


class Sphere(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    title: Mapped[str] = mapped_column(String)
    duration: Mapped[int] = mapped_column(Integer, default=30)
    best_time: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    def as_dict(self):
        return {
            "title": self.title,
            "duration": self.duration,
            "best_time": self.best_time,
            "description": self.description
        }


class SphereUser(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    web_user_id: Mapped[int] = mapped_column(ForeignKey("webuser.id"))
    order: Mapped[int] = mapped_column(Integer, default=0)
    depth: Mapped[int] = mapped_column(Integer, default=2)
    sphere_id: Mapped[int] = mapped_column(ForeignKey("sphere.id"))
    sphere = relationship("Sphere", lazy="selectin")
