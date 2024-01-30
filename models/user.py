from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, String, DateTime, func, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped

from db.base_class import Base

if TYPE_CHECKING:
    from .practise import Practise # Noqa
    from .media import Media # Noqa


class User(Base):
    id = Column(BigInteger, primary_key=True, index=True, unique=True)
    tg_id = Column(BigInteger, index=True, unique=True)
    username = Column(String)
    fullname = Column(String)
    email = Column(String, unique=True)
    contact = Column(String)
    create_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, onupdate=func.now())
    last_visit = Column(DateTime)
    internal_amount = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    payments = relationship("UserPayment", back_populates="user", cascade="all, delete-orphan")
    full_access_granted: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "tg_id": self.tg_id,
            "username": self.username,
            "fullname": self.fullname,
            "email": self.email,
            "contact": self.contact,
            "internal_amount": self.internal_amount,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "full_access_granted": datetime.timestamp(self.full_access_granted) if self.full_access_granted else None,
        }


class Invoice(Base):
    id = Column(BigInteger, primary_key=True, index=True, unique=True)
    uuid = Column(String)
    create_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, onupdate=func.now())
    practise_id: Mapped[int] = mapped_column(ForeignKey("practise.id", ondelete='SET NULL'))
    media_id: Mapped[int] = mapped_column(ForeignKey("media.id", ondelete='SET NULL'), nullable=True)
    amount = Column(BigInteger)
    status = Column(String(32), default="CREATED") # CREATED|PAID
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    valid_to = Column(DateTime, nullable=True)
    ticket_count: Mapped[int] = mapped_column(Integer, nullable=True)
    category: Mapped[int] = mapped_column(Integer, default=1)

    payment = relationship("UserPayment", back_populates="invoice", lazy="selectin", cascade="all, delete-orphan")
    user = relationship("User", lazy="selectin")
    media = relationship("Media", lazy="selectin")
    practise = relationship("Practise", lazy="selectin")

    def as_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "practise_id": self.practise_id,
            "media_id": self.media_id,
            "amount": self.amount,
            "status": self.status,
            "user_id": self.user_id,
            "valid_to": self.valid_to,
            "ticket_count": self.ticket_count,
            "category": self.category,
        }


class UserPayment(Base):
    id = Column(BigInteger, primary_key=True, index=True, unique=True)
    paid_amount = Column(BigInteger)
    user_id = mapped_column(ForeignKey("user.id"))
    media_id = mapped_column(ForeignKey("media.id", ondelete='SET NULL'))
    practise_id = mapped_column(ForeignKey("practise.id", ondelete='SET NULL'))
    create_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, onupdate=func.now())
    invoice_id = mapped_column(ForeignKey("invoice.id", ondelete='SET NULL'))

    user = relationship("User", back_populates="payments", lazy="selectin")
    media = relationship("Media", lazy="selectin")
    practise = relationship("Practise", lazy="selectin")
    invoice = relationship("Invoice", back_populates="payment", uselist=False, lazy="selectin")

    def as_dict(self):
        return {
            "id": self.id,
            "paid_amount": self.paid_amount,
            "practise_id": self.practise_id,
            "invoice_id": self.invoice_id,
            "user_id": self.user_id,
        }
