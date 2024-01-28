from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.practise import Practise
from schemas.practise import PractiseCreate, PractiseUpdate
from utils.constants import MessageTypes, PractiseCategories


class CRUDPractise(CRUDBase[Practise, PractiseCreate, PractiseUpdate]):
    async def get_practises_by_order(
            self,
            db: AsyncSession,
            only_published: bool = False
    ) -> List[ModelType]:
        if only_published:
            result = await db.execute(select(self.model).filter(self.model.is_published.is_(True)).order_by(
                self.model.order)
            )
        else:
            result = await db.execute(select(self.model).order_by(self.model.order))
        return result.scalars().all()

    async def get_last_order(self, db: AsyncSession) -> int:
        practise = (await db.execute(func.max(self.model.order))).scalars().one()
        if not practise:
            return 1
        else:
            return practise+1

    async def update_media_group_id(self, db: AsyncSession, practise_id: int, media_group_id: int):
        practise = await self.get(db, id=practise_id)
        if practise.media_group_id == media_group_id:
            return practise
        else:
            practise.media_group_id = media_group_id
            practise.media_type = MessageTypes.MEDIA_GROUP.value
            db.add(practise)
            await db.commit()
            await db.refresh(practise)
            return practise

    async def get_online_practise(
            self,
            db: AsyncSession
    ) -> List[ModelType]:

        result = await db.execute(select(self.model).filter(self.model.category == PractiseCategories.ONLINE.value))

        return result.scalars().first()


crud_practise = CRUDPractise(Practise)
