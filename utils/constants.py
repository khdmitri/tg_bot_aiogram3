from aiogram.types import Update
from enum import Enum


class MessageTypes(Enum):
    PHOTO = 1
    VIDEO = 2
    MEDIA_GROUP = 3
    TEXT_MESSAGE = 4
    NOT_DEFINED = 0


class PractiseCategories(Enum):
    LESSON = 1
    ONLINE = 2


BOT_INSTANCE = {
    "instance": None
}

ALL_UPDATES = [
    "message", "edited_message", "channel_post", "edited_channel_post", "message_reaction", "message_reaction_count",
    "inline_query", "chosen_inline_result", "callback_query", "shipping_query", "pre_checkout_query", "poll",
    "poll_answer", "my_chat_member", "chat_member", "chat_join_request", "chat_boost", "removed_chat_boost",
]
