import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, InputFile, FSInputFile
from aiogram.utils.markdown import hbold

# Bot token can be obtained via https://t.me/BotFather
from aiogram.utils.token import TokenValidationError
from redis.asyncio import Redis

from core import config
from core.config import settings
from tg_bot.handlers.commands import router_commands
from utils import get_logger
# from handlers import router

TOKEN = settings.BOT_TOKEN

# All handlers should be attached to the Router (or Dispatcher)
if settings.USE_REDIS:
    redis_client = Redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/tg_bot")
    storage = RedisStorage(redis=redis_client)
else:
    storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    # intro_file: InputFile = FSInputFile('media/intro/intro.mp4', filename='intro.mp4')
    await message.answer_video("BAACAgIAAxkBAAEoyclln4wCRLj4HwABFHjsRziT0IsU2MAAAm46AAJOEQFJKhIqccGQFqg0BA")
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    try:
        bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
        dp.include_router(router_commands)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except TokenValidationError:
        logger.error("Token is invalid")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = get_logger()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot Stopped!")
