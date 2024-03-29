from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.blog import Blog
from schemas import BlogCreate, BlogUpdate


class CRUDBlog(CRUDBase[Blog, BlogCreate, BlogUpdate]):
    async def get_multi(
            self, db: AsyncSession, *, skip: int = 0, limit: int = 50
    ) -> List[Blog]:
        result = await db.execute(select(self.model).offset(skip).limit(limit).order_by(self.model.id.desc()))
        return result.scalars().all()


crud_blog = CRUDBlog(Blog)
