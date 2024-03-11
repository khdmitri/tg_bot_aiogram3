import traceback

from aiogram import types
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatMemberUpdated

from crud import crud_user, crud_practise, crud_invoice
from db.session import SessionLocalAsync
from utils.logger import get_logger

logger = get_logger()

MAIN_CHANNEL_ID = -1002112555471


async def check_access_right(update: types.ChatJoinRequest):
    chat = update.chat
    logger.info(f"JoinUserToChat ID: {chat.id}")
    user_tg = update.from_user
    logger.info(f"User ID: {user_tg.id}")
    async with SessionLocalAsync() as db:
        user = await crud_user.get_by_tg_id_or_create(db, tg_id=user_tg.id)
        if user:
            practise = await crud_practise.get_practise_by_channel_id(db=db, channel_id=chat.id)
            if practise:
                total_cost = 0
                for media in practise.medias:
                    total_cost += media.cost
                if total_cost > 0:
                    invoice = await crud_invoice.get_valid_channel_invoice(db, user_id=user.id, practise_id=practise.id)
                    if invoice:
                        await update.approve()
                    else:
                        logger.warning("Invoice not found")
                        await update.decline()
                else:
                    logger.info("Practise has no commercial lessons, check if chat member...")
                    bot = update.bot
                    try:
                        chat_member = await bot.get_chat_member(chat_id=MAIN_CHANNEL_ID, user_id=user.tg_id)
                        logger.info(f"Received ChatMember: {chat_member}")
                        if chat_member and chat_member.status == ChatMemberStatus.MEMBER:
                            await update.approve()
                        else:
                            logger.info(f"CHAT MEMBER HAS NO STATUS {ChatMemberStatus.MEMBER} because it is {chat_member.status}")
                            await bot.send_message(update.user_chat_id,
                                                   text="К сожалению, Вы не подписаны на наш канал: https://t.me/yoga_master_mind.\n" +
                                                        "Подпишитесь на наш канал и попробуйте снова.")
                            await update.decline()
                    except TelegramBadRequest:
                        logger.error(traceback.format_exc())
                        await bot.send_message(update.user_chat_id,
                                               text="К сожалению, Вы не подписаны на наш канал: https://t.me/yoga_master_mind.\n" +
                                                    "Подпишитесь на наш канал и попробуйте снова.")
            else:
                logger.warning("Practise is invalid")
                await update.decline()
        else:
            logger.warning("User is invalid")
            await update.decline()
