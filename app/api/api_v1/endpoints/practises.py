from typing import List, Any, Union

from aiogram import Dispatcher, Bot
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, SentWebAppMessage
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from crud import crud_practise
from schemas import Practise
from bot import bot
from utils.invoice import Invoice

router = APIRouter()

FULL_PRACTISE_DISCOUNT = 20


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


@router.post("/webapp_data")
async def webapp_data_action(
        *,
        data: schemas.WebAppData
) -> Union[str | None]:
    """
    Process webapp_data.
    """
    invoice_inst = Invoice(user={"tg_id": data.user_id}, practise_id=data.order_id, lesson=None, message=None)
    link = await invoice_inst.create_invoice_link(bot=bot, discount=FULL_PRACTISE_DISCOUNT)
    return link
