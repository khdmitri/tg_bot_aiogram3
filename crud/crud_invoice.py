from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.user import Invoice
from schemas.invoice import InvoiceCreate, InvoiceUpdate
from utils.constants import PractiseCategories


class CRUDInvoice(CRUDBase[Invoice, InvoiceCreate, InvoiceUpdate]):
    async def get_paid_invoice(self,
                               db: AsyncSession, practise_id: int, media_id: int
                               ) -> Invoice:
        result = await db.execute(select(Invoice).filter(
            Invoice.practise_id == practise_id,
            Invoice.media_id == media_id,
            Invoice.status == 'PAID',
            Invoice.valid_to >= datetime.now()
        ))
        return result.scalars().first()

    async def get_online_invoice(self, db: AsyncSession, user_id: int) -> Invoice:
        result = await db.execute(select(Invoice).filter(Invoice.user_id == user_id,
                                                         Invoice.category == PractiseCategories.ONLINE.value
                                                         ))
        return result.scalars().first()

    async def get_valid_online_invoice(self, db: AsyncSession, user_id: int) -> Invoice:
        result = await db.execute(select(Invoice).filter(Invoice.user_id == user_id,
                                                         Invoice.category == PractiseCategories.ONLINE.value,
                                                         Invoice.status == 'PAID',
                                                         Invoice.ticket_count > 0
                                                         ))
        return result.scalars().first()


    async def get_invoice_by_uuid(self, db: AsyncSession, uuid: str) -> Invoice:
        result = await db.execute(select(Invoice).filter(Invoice.uuid == uuid))
        return result.scalars().first()


crud_invoice = CRUDInvoice(Invoice)
