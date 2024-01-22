import uuid
from datetime import datetime

from aiogram.types import Message

from data import config
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU


class Invoice:
    def __init__(self, *, user: dict, practise_id: int, lesson: dict, message: Message):
        self.user = user
        self.practise_id = practise_id,
        self.lesson = lesson
        self.message = message

    async def send_invoice(self, valid_to: int):
        invoice_id = str(uuid.uuid4())
        payload = {
            "title": self.lesson["title"],
            "description": LEXICON_DEFAULT_NAMES_RU['payment_description'],
            "payload": invoice_id + ":::" + str(valid_to),
            "provider_token": config.UKASSA_PROVIDER_TOKEN_TEST,
            "currency": "RUB",
            "start_parameter": "test",
            "prices": [{
                "label": "руб",
                "amount": int(str(self.lesson["cost"])+"00")
            }]
        }
        await self.message.answer_invoice(**payload)