from typing import List, Any, Union

from aiogram import Dispatcher, Bot
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, SentWebAppMessage
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from crud import crud_practise, crud_invoice, crud_user, crud_media, crud_group
from db.session import SessionLocalAsync
from models.group import Group
from models.media import Media
from models.user import User
from schemas import Practise, GroupCreate
from bot import bot
from utils.constants import WEBAPP_ACTIONS
from utils.invoice import Invoice
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()

FULL_PRACTISE_DISCOUNT = 20
ABONEMENT_DISCOUNT = 20


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
        db: AsyncSession = Depends(deps.get_db_async),
        *,
        data: schemas.WebAppData
) -> Union[str | None]:
    """
    Process webapp_data.
    """
    match data.action:
        case WEBAPP_ACTIONS.buy_practise.value:
            invoice_inst = Invoice(user={"tg_id": data.user_id}, practise_id=data.order_id, lesson=None, message=None)
            link = await invoice_inst.create_invoice_link(bot=bot, action=data.action, discount=FULL_PRACTISE_DISCOUNT)
            return link
        case WEBAPP_ACTIONS.buy_online.value:
            practise_online = await crud_practise.get_online_practise(db)
            lesson = await crud_media.get(db, id=data.order_id)
            invoice_inst = Invoice(user={"tg_id": data.user_id}, practise_id=practise_online.id,
                                   lesson=lesson.as_dict(), message=None, is_online=True)
            link = await invoice_inst.create_invoice_link(bot=bot, action=data.action, discount=0)
            return link
        case WEBAPP_ACTIONS.buy_abonement.value:
            practise_online = await crud_practise.get_online_practise(db)
            invoice_inst = Invoice(user={"tg_id": data.user_id}, practise_id=practise_online.id,
                                   lesson=None, message=None, is_online=True)
            link = await invoice_inst.create_invoice_link(bot=bot, action=data.action, discount=ABONEMENT_DISCOUNT)
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
) -> List[schemas.MediaBase]:
    """
    Retrieve practises online.
    """
    practise = await crud_practise.get_online_practise(db)
    practises = await crud_media.get_online_by_practise_id(db, practise_id=practise.id)
    return practises


@router.post("/get_paid_invoice_online")
async def get_paid_invoice_online(
        *,
        db: AsyncSession = Depends(deps.get_db_async),
        data: schemas.UserByTgId
) -> schemas.Invoice | None:
    """
    Search for paid online invoice.
    """
    user = await crud_user.get_by_tg_id(db, tg_id=data.tg_id)
    if user:
        return await crud_invoice.get_valid_online_invoice(db, user_id=user.id)
    return None


@router.post("/is_group_member")
async def if_user_group_member(
        *,
        db: AsyncSession = Depends(deps.get_db_async),
        data: schemas.UserGroupMember
) -> schemas.Group | None:
    """
    Search for group member.
    """
    user = await crud_user.get_by_tg_id(db, tg_id=data.tg_id)
    if user:
        return await crud_group.is_member(db, user_id=user.id, media_id=data.media_id)
    return None


async def _join_to_group(*, media: Media, user: User, db):
    if media.is_free:
        group_schema = GroupCreate(**{
            "user_id": user.id,
            "media_id": media.id
        })
        return await crud_group.create(db, obj_in=group_schema)


@router.post("/join_group_online")
async def add_user_group(
        *,
        db: AsyncSession = Depends(deps.get_db_async),
        data: schemas.UserGroupMember
) -> schemas.Group | None:
    """
    Search for group member.
    """
    user = await crud_user.get_by_tg_id(db, tg_id=data.tg_id)
    media = await crud_media.get(db, id=data.media_id)
    if user:
        if media.is_free:
            return await _join_to_group(db=db, media=media, user=user)
        else:
            invoice = await crud_invoice.get_valid_online_invoice(db, user_id=user.id)
            if invoice:
                invoice.ticket_count -= 1
                db.add(invoice)
                await db.commit()
                await db.refresh(invoice)
                return await _join_to_group(db=db, media=media, user=user)
    return None


@router.post("/leave_group_online")
async def remove_user_group(
        *,
        db: AsyncSession = Depends(deps.get_db_async),
        data: schemas.UserGroupMember
) -> bool:
    lesson = await crud_media.get(db, id=data.media_id)
    user = await crud_user.get_by_tg_id(db, tg_id=data.tg_id)
    if not lesson.is_free:
        invoice = await crud_invoice.get_online_invoice(db, user.id)
        if invoice and invoice.status == 'PAID':
            invoice.ticket_count += 1
            db.add(invoice)
            await db.commit()
            await db.refresh(invoice)
    member: Group = await crud_group.is_member(db, user_id=user.id, media_id=lesson.id)
    if member:
        await crud_group.remove(db, id=member.id)

    return True
