from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.media import Media
from schemas.media import MediaCreate, MediaUpdate


class CRUDMedia(CRUDBase[Media, MediaCreate, MediaUpdate]):
    async def get_multi_by_practise_id(
            self,
            db: AsyncSession,
            practise_id: int
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).filter(
            self.model.practise_id == practise_id).order_by(
            self.model.order)
        )
        return result.scalars().all()

    async def get_last_order(self, db: AsyncSession) -> int:
        media_order: int = (await db.execute(func.max(self.model.order))).scalars().one()
        if not media_order:
            return 1
        else:
            return media_order+1


crud_media = CRUDMedia(Media)
