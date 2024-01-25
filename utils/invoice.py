import uuid
from datetime import datetime, timedelta

from aiogram.types import Message

from crud import crud_invoice
from data import config
from db.session import SessionLocalAsync
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU
from schemas import InvoiceCreate

CURRENCY_STEP = {
    "RUB": 100,
}


class Invoice:
    def __init__(self, *, user: dict, practise_id: int, lesson: dict, message: Message):
        self.user = user
        self.practise_id = practise_id,
        self.lesson = lesson
        self.message = message

    async def send_invoice(self, valid_to: int):
        invoice_id = str(uuid.uuid4())
        amount = self.lesson["cost"]*CURRENCY_STEP["RUB"]
        payload = {
            "title": self.lesson["title"],
            "description": LEXICON_DEFAULT_NAMES_RU['payment_description'],
            "payload": invoice_id,
            "provider_token": config.UKASSA_PROVIDER_TOKEN_LIVE,
            "currency": "RUB",
            "start_parameter": "test",
            "prices": [{
                "label": "руб",
                "amount": amount
            }]
        }
        invoice_schema = InvoiceCreate(**{
            'uuid': invoice_id,
            'practise_id': self.lesson['practise_id'],
            'media_id': self.lesson['id'],
            'amount': amount,
            'status': 'CREATED',
            'user_id': self.user['id'],
            'valid_to': datetime.now() + timedelta(days=valid_to*30)
        })
        async with SessionLocalAsync() as db:
            invoice = await crud_invoice.create(db, obj_in=invoice_schema)
            if invoice:
                await self.message.answer_invoice(**payload)
            else:
                await self.message.answer(text=LEXICON_DEFAULT_NAMES_RU['payment_error'])
