from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

from utils import log_message


class MessageLoggerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        message: Optional[Message] = None
        if event.message is not None:
            message = event.message
        elif event.callback_query is not None:
            message = event.callback_query.message

        if message is not None:
            await log_message.add_message_id(message.chat.id, message_id=message.message_id)

        return await handler(event, data)
