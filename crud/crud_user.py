from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.user import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_tg_id(self, db: AsyncSession, tg_id: Any) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.tg_id == tg_id))
        return result.scalars().first()


crud_user = CRUDUser(User)
