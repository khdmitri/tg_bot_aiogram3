import uuid
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot
from aiogram.types import Message, LabeledPrice
from sqlalchemy.ext.asyncio import AsyncSession

from crud import crud_invoice, crud_practise
from data import config
from db.session import SessionLocalAsync
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU
from schemas import InvoiceCreate
from utils.constants import PractiseCategories

CURRENCY_STEP = {
    "RUB": 100,
}

DISCOUNT = 0.9
COST = 300
TITLE = 'ONLINE-Урок'


class Invoice:
    def __init__(self, *, user: dict,
                 practise_id: int,
                 lesson: dict | None,
                 message: Message | None,
                 is_online: bool = False,
                 ticket_count: int = 1):
        self.user = user
        self.practise_id = practise_id
        self.lesson = lesson if lesson is not None else {
            "cost": COST,
            "title": TITLE,
        }
        self.message = message
        self.ticket_count = ticket_count
        self.is_online = is_online

    async def _get_or_create_invoice(self, db: AsyncSession, *, amount: int, invoice_id: str,
                                     valid_to: Optional[int] = None):
        invoice = await crud_invoice.get_online_invoice(db, user_id=self.user["id"])
        if invoice:
            invoice.status = "CREATED"
            invoice.ticket_count = self.ticket_count
            db.add(invoice)
            await db.commit()
            await db.refresh(invoice)
        else:
            invoice = await self._create_invoice(db, amount=amount, invoice_id=invoice_id)

        return invoice

    async def _create_invoice(self, db: AsyncSession, *, amount: int, invoice_id: str, valid_to: Optional[int] = None):
        invoice_schema = InvoiceCreate(**{
            'uuid': invoice_id,
            'practise_id': self.practise_id,
            'media_id': self.lesson.get("id", None),
            'amount': amount,
            'status': 'CREATED',
            'user_id': self.user['id'],
            'valid_to': datetime.now() + timedelta(days=valid_to * 30) if valid_to else None,
            'ticket_count': self.ticket_count,
            'category': PractiseCategories.ONLINE.value if self.is_online else PractiseCategories.LESSON.value
        })

        return await crud_invoice.create(db, obj_in=invoice_schema)

    async def send_invoice(self, valid_to: Optional[int] = None):
        invoice_id = str(uuid.uuid4())
        amount = self.lesson["cost"]*CURRENCY_STEP["RUB"]*self.ticket_count
        if self.ticket_count > 1:
            amount = int(amount*DISCOUNT)
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
        async with SessionLocalAsync() as db:
            if self.is_online:
                invoice = await self._get_or_create_invoice(db, amount=amount, invoice_id=invoice_id)
            else:
                invoice = await self._create_invoice(db, amount=amount, invoice_id=invoice_id, valid_to=valid_to)
            if invoice:
                await self.message.answer_invoice(**payload)
            else:
                await self.message.answer(text=LEXICON_DEFAULT_NAMES_RU['payment_error'])

    async def create_invoice_link(self, bot: Bot, discount: int = 0):
        async with SessionLocalAsync() as db:
            practise = await crud_practise.get(db, id=self.practise_id)
            if practise:
                medias = practise.medias
                total = 0
                for media in medias:
                    if not media.is_free:
                        total += media.cost
                if total > 0:
                    lPrice: LabeledPrice = LabeledPrice(label="руб", amount=int(total - total*discount/100)*CURRENCY_STEP["RUB"])
                    prices = [lPrice]
                    link = await bot.create_invoice_link(title=practise.title, description=practise.description,
                                                         payload=str(uuid.uuid4())+"::"+"1"+"::"+self.user["tg_id"],
                                                         provider_token=config.UKASSA_PROVIDER_TOKEN_LIVE,
                                                         currency="RUB",
                                                         prices=prices)
                    print("LINK:", link)
                    return link
        return None
