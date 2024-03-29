from datetime import datetime
from typing import Any, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.user import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_tg_id(self, db: AsyncSession, tg_id: Any) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.tg_id == tg_id))
        return result.scalars().first()

    async def get_by_tg_id_or_create(self, db: AsyncSession, tg_id: Any) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.tg_id == tg_id))
        user = result.scalars().first()
        if user:
            return user
        else:
            new_user = UserCreate(tg_id=tg_id,
                                  last_visit=datetime.now(),
                                  is_active=True,
                                  is_admin=False)
            user = await crud_user.create(db, obj_in=new_user)
            return user

    async def get_admins(self, db: AsyncSession) -> List[User]:
        result = await db.execute(select(User).filter(User.is_admin.is_(True)))
        return result.scalars().all()


crud_user = CRUDUser(User)
