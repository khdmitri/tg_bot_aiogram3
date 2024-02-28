from typing import List, Any, Union

from aiogram import Dispatcher, Bot
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, SentWebAppMessage
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from crud import crud_practise, crud_invoice, crud_user, crud_media
from models.user import Invoice
from schemas import Practise
from bot import bot
from utils.invoice import Invoice
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()

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


@router.post("/get_paid_invoice")
async def get_paid_invoice(
        *,
        db: AsyncSession = Depends(deps.get_db_async),
        data: schemas.PractisePaidRequest
) -> schemas.Invoice | None:
    """
    Search for paid invoice.
    """
    user = await crud_user.get_by_tg_id(db, tg_id=data.tg_id)
    logger.info(f"Got User: {user}")
    if user:
        return await crud_invoice.get_paid_invoice(db, practise_id=data.practise_id, media_id=None, user_id=user.id)
    return None


@router.get("/online", response_model=List[schemas.Media])
async def read_practises_online(
        db: AsyncSession = Depends(deps.get_db_async)
) -> List[Practise]:
    """
    Retrieve practises online.
    """
    practise = await crud_practise.get_online_practise(db)
    practises = await crud_media.get_online_by_practise_id(db, practise_id=practise.id)
    return practises
