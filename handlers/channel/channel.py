from aiogram import types
from aiogram.types import ChatMemberUpdated

from utils.logger import get_logger

logger = get_logger()


async def check_access_right(update: types.ChatJoinRequest):
    chat = update.chat
    user = update.from_user
    logger.info(f"Received request from chat={chat.id} from user={user.id}")
    await update.approve()
