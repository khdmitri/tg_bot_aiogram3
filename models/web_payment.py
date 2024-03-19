from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base

if TYPE_CHECKING:
    from .web_user import WebUser # Noqa
    from .practise import Practise  # Noqa


class WebPayment(Base):
    payment_id: Mapped[str] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    web_user_id: Mapped[int] = mapped_column(ForeignKey("webuser.id"))
    web_user = relationship("WebUser", lazy="selectin")
    status: Mapped[int] = mapped_column(Integer, default=0)
    practise_id: Mapped[int] = mapped_column(ForeignKey("practise.id"))
    practise = relationship("Practise", lazy="selectin")
    create_date = mapped_column(DateTime, server_default=func.now())
    update_date = mapped_column(DateTime, onupdate=func.now())
    amount = mapped_column(Integer, default=0)
