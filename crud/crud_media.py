from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.media import Media
from schemas.media import MediaCreate, MediaUpdate
from utils.constants import MessageTypes


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

    async def update_media_group_id(self, db: AsyncSession, media_id: int, media_group_id: int):
        media = await self.get(db, id=media_id)
        if media.media_group_id == media_group_id:
            return media
        else:
            media.media_group_id = media_group_id
            media.media_type = MessageTypes.MEDIA_GROUP.value
            db.add(media)
            await db.commit()
            await db.refresh(media)
            return media


crud_media = CRUDMedia(Media)
