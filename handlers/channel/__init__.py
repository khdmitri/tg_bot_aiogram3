from aiogram import Router, F
from aiogram.enums import ContentType

from handlers.channel import channel


def prepare_router() -> Router:
    channel_router = Router()

    channel_router.chat_join_request.register(channel.check_access_right)

    return channel_router
