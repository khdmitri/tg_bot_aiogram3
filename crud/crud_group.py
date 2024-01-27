from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.group import Group
from schemas import GroupCreate, GroupUpdate


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    async def get_group_by_media_id(
            self,
            db: AsyncSession,
            media_id: int
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).filter(
            self.model.media_id == media_id)
        )
        return result.scalars().all()

    async def is_member(self, db: AsyncSession, *, user_id: int, media_id: int):
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id,
                                                            self.model.media_id == media_id))

        if result:
            return result.scalars().first()
        else:
            return False


crud_group = CRUDGroup(Group)
