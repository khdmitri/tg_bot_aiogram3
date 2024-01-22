import asyncio
import functools

from aiogram.types import Message
from redis.asyncio import Redis

from data import config


class LogMessage:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_message_id(self, chat_id: int, message_id: int):
        key_name = f'ml_{chat_id}'
        data = await self.redis.get(key_name)
        if not data:
            message_ids = str(message_id)
        else:
            data = str(data.decode()) if isinstance(data, bytes) else data
            message_ids = [int(el) for el in data.split(",")]
            if message_id not in message_ids:
                message_ids.append(message_id)
            message_ids = ",".join([str(i) for i in message_ids])

        await self.redis.set(key_name, message_ids)

    async def add_message(self, message: Message | list):
        if isinstance(message, Message):
            await self.add_message_id(chat_id=message.chat.id, message_id=message.message_id)
        elif isinstance(message, list):
            for msg in message:
                await self.add_message_id(chat_id=msg.chat.id, message_id=msg.message_id)

    async def clean_content(self, chat_id: int, context: Message):
        key_name = f'ml_{chat_id}'
        data = await self.redis.get(key_name)
        if data:
            data = str(data.decode()) if isinstance(data, bytes) else data
            message_ids = [int(el) for el in data.split(",")]
            await context.bot.delete_messages(chat_id=chat_id, message_ids=message_ids)
            await self.redis.delete(key_name)


log_message = LogMessage(redis=Redis(
        host=config.FSM_HOST,
        password=config.FSM_PASSWORD,
        port=config.FSM_PORT,
        db=1,
    ))
