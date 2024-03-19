from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.web_payment import WebPayment
from schemas.web_payment import WebPaymentCreate, WebPaymentUpdate


class CRUDWebPayment(CRUDBase[WebPayment, WebPaymentCreate, WebPaymentUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[WebPayment]:
        result = await db.execute(select(self.model).filter(self.model.payment_id == id))
        return result.scalars().first()


crud_web_payment = CRUDWebPayment(WebPayment)
