from typing import Any, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.sphere import SphereUser
from schemas import SphereUserCreate, SphereUserUpdate


class CRUDSphereUser(CRUDBase[SphereUser, SphereUserCreate, SphereUserUpdate]):
    async def get_by_user_id(self, db: AsyncSession, user_id: Any) -> List[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.web_user_id == user_id).order_by(
            self.model.sphere_id))
        return result.scalars().all()

    async def clean_by_user_id(self, db: AsyncSession, user_id: Any) -> bool:
        await db.execute(delete(self.model).where(self.model.web_user_id == user_id))
        await db.commit()
        return True


crud_sphere_user = CRUDSphereUser(SphereUser)
