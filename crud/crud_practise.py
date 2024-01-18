from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.practise import Practise
from schemas.practise import PractiseCreate, PractiseUpdate


class CRUDPractise(CRUDBase[Practise, PractiseCreate, PractiseUpdate]):
    async def get_practises_by_order(
            self,
            db: AsyncSession
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).order_by(self.model.order))
        return result.scalars().all()

    async def get_last_order(self, db: AsyncSession) -> int:
        practise = (await db.execute(func.max(self.model.order))).scalars().one()
        if not practise:
            return 1
        else:
            return practise+1


crud_practise = CRUDPractise(Practise)
