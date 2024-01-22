from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.user import Invoice
from schemas.invoice import InvoiceCreate, InvoiceUpdate


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
        return result.scalars().all()


crud_invoice = CRUDInvoice(Invoice)
