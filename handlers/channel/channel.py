from aiogram import types
from aiogram.types import ChatMemberUpdated

from crud import crud_user, crud_practise, crud_invoice
from db.session import SessionLocalAsync
from utils.logger import get_logger

logger = get_logger()


async def check_access_right(update: types.ChatJoinRequest):
    chat = update.chat
    user = update.from_user
    async with SessionLocalAsync() as db:
        user = await crud_user.get_by_tg_id(db, tg_id=user.id)
        if user:
            practise = await crud_practise.get_practise_by_channel_id(channel_id=chat.id)
            if practise:
                invoice = await crud_invoice.get_valid_channel_invoice(db, user_id=user.id, practise_id=practise.id)
                if invoice:
                    await update.approve()
                else:
                    logger.warning("Invoice not found")
                    await update.decline()
            else:
                logger.warning("Practise is invalid")
                await update.decline()
        else:
            logger.warning("User is invalid")
            await update.decline()
