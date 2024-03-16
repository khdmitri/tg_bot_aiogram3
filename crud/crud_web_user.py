from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.web_user import WebUser
from schemas import WebUserCreate, WebUserUpdate


class CRUDWebUser(CRUDBase[WebUser, WebUserCreate, WebUserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[WebUser]:
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()


crud_web_user = CRUDWebUser(WebUser)
