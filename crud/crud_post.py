from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase, ModelType
from models.post import Post
from schemas.post import PostCreate, PostUpdate
from utils.constants import MessageTypes


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    async def get_posts_by_page(
            self,
            db: AsyncSession,
            page: str
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.page == page).order_by(self.model.order))
        return result.scalars().all()

    async def get_last_order(self, db: AsyncSession) -> int:
        post = (await db.execute(func.max(self.model.order))).scalars().one()
        if not post:
            return 10
        else:
            return post+10

    async def update_media_group_id(self, db: AsyncSession, post_id: int, media_group_id: int):
        post = await self.get(db, id=post_id)
        if post.media_group_id == media_group_id:
            return post
        else:
            post.media_group_id = media_group_id
            post.message_type = MessageTypes.MEDIA_GROUP.value
            db.add(post)
            await db.commit()
            await db.refresh(post)
            return post


crud_post = CRUDPost(Post)
