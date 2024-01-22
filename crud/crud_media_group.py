from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.media import Media
from models.media_group import MediaGroup
from schemas import MediaGroupCreate, MediaGroupUpdate
from schemas.media import MediaCreate, MediaUpdate


class CRUDMediaGroup(CRUDBase[MediaGroup, MediaGroupCreate, MediaGroupUpdate]):
    async def get_multi_by_media_group_id(
            self,
            db: AsyncSession,
            media_group_id: int
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).filter(
            self.model.media_group_id == media_group_id)
        )
        return result.scalars().all()


crud_media_group = CRUDMediaGroup(MediaGroup)
