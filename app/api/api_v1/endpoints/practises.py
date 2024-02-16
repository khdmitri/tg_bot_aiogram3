from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from crud import crud_practise
from schemas import Practise

router = APIRouter()


@router.get("/", response_model=List[schemas.Practise])
async def read_practises(
    db: AsyncSession = Depends(deps.get_db_async),
    skip: int = 0,
    limit: int = 100,
) -> List[Practise]:
    """
    Retrieve practises.
    """
    practises = await crud_practise.get_practises_by_order(db, only_published=True, include_online=False)
    return practises
