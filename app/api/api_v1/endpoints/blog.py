from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from crud import crud_blog
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=List[schemas.Blog])
async def read_blogs(
        db: AsyncSession = Depends(deps.get_db_async),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    Retrieve blogs.
    """
    blogs = await crud_blog.get_multi(db, skip=skip, limit=limit)
    return blogs
