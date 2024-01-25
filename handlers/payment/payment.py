from aiogram.fsm.context import FSMContext
from aiogram.types import PreCheckoutQuery, Message

from crud import crud_invoice
from db.session import SessionLocalAsync
from handlers.user.lesson import view_lesson
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU
from utils import log_message, text_decorator


async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    invoice_uuid = pre_checkout_q.invoice_payload
    async with SessionLocalAsync() as db:
        invoice = await crud_invoice.get_invoice_by_uuid(db, uuid=invoice_uuid)
        if invoice:
            if invoice.amount <= pre_checkout_q.total_amount:
                await pre_checkout_q.answer(ok=True)
            else:
                await pre_checkout_q.answer(ok=False)
        else:
            await pre_checkout_q.answer(ok=False)


async def successful_payment(message: Message, state: FSMContext):
    payment_info = message.successful_payment
    invoice_uuid = payment_info.invoice_payload
    async with SessionLocalAsync() as db:
        invoice_db = await crud_invoice.get_invoice_by_uuid(db, uuid=invoice_uuid)
        if invoice_db:
            invoice_db.status = 'PAID'
            db.add(invoice_db)
            await db.commit()
            await db.refresh(invoice_db)
            await log_message.add_message(
                await message.answer(text=text_decorator.strong(LEXICON_DEFAULT_NAMES_RU['payment_success'])))
        else:
            await log_message.add_message(
                await message.answer(
                    text=text_decorator.strong(f'Мы не смогли завершить платеж корректно, но не переживайте, '
                                               'мы получили платеж и сможем Вам помочь. '
                                               f'Напишите нам сообщение о проблеме и укажите этот номер: {invoice_uuid}')))

    await view_lesson(message, state)
