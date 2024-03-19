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

    async def get_by_email_or_create(self, db: AsyncSession, email: str) -> Optional[WebUser]:
        web_user = await self.get_by_email(db, email)
        if web_user:
            return web_user
        else:
            new_web_user = WebUserCreate(email=email)
            web_user = await crud_web_user.create(db, obj_in=new_web_user)
            return web_user


crud_web_user = CRUDWebUser(WebUser)
