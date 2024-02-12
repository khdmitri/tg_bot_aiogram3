from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# id = Column(BigInteger, primary_key=True, index=True, unique=True)
# uuid = Column(String)
# create_date = Column(DateTime, server_default=func.now())
# update_date = Column(DateTime, onupdate=func.now())
# practise_id: Mapped[int] = mapped_column(ForeignKey("practise.id"))
# media_id: Mapped[int] = mapped_column(ForeignKey("media.id"))
# amount = Column(BigInteger)
# status = Column(String(32), default="CREATED") # CREATED|PAID
# user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#
# payment = relationship("UserPayment", back_populates="invoice", lazy="selectin")
# user = relationship("User", lazy="selectin")
# media = relationship("Media", lazy="selectin")
# practise = relationship("Practise", lazy="selectin")


class InvoiceBase(BaseModel):
    uuid: str
    practise_id: int
    media_id: Optional[int] = None
    amount: int
    status: str
    user_id: int


class InvoiceCreate(InvoiceBase):
    valid_to: Optional[datetime] = None
    ticket_count: int = 1
    category: int


class InvoiceUpdate(InvoiceBase):
    id: int


class InvoiceInDBBase(InvoiceUpdate):
    class Config:
        from_attributes = True


# Additional properties stored in DB
class InvoiceInDB(InvoiceInDBBase):
    pass


class Invoice(InvoiceInDBBase):
    create_date: datetime
    update_date: datetime
