from aiogram.fsm.context import FSMContext
from aiogram.types import PreCheckoutQuery, Message

from crud import crud_invoice, crud_user, crud_practise
from db.session import SessionLocalAsync
from handlers.user.core import user_message_handler
from handlers.user.lesson import view_lesson, join_online_lesson
from handlers.user.start import home
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU
from utils import log_message, text_decorator
from utils.constants import PractiseCategories
from utils.invoice import Invoice

PRACTISE_VALID_TO = 2 # months


async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    invoice_uuid = pre_checkout_q.invoice_payload.split("::")
    if len(invoice_uuid) > 1:
        await pre_checkout_q.answer(ok=True)
    else:
        invoice_uuid = invoice_uuid[0]
        async with SessionLocalAsync() as db:
            invoice = await crud_invoice.get_invoice_by_uuid(db, uuid=invoice_uuid)
            if invoice:
                if invoice.amount <= pre_checkout_q.total_amount:
                    await pre_checkout_q.answer(ok=True)
                else:
                    await pre_checkout_q.answer(ok=False)
            else:
                await pre_checkout_q.answer(ok=False)


async def successful_payment(message: Message, state: FSMContext, user: dict):
    payment_info = message.successful_payment
    res = payment_info.invoice_payload.split("::")
    if len(res) > 1:
        invoice_uuid = res[0]
        practise_id = int(res[1])
        tg_id = int(res[2])

        # 1 Get User by tg_id or create a new one
        async with SessionLocalAsync() as db:
            user = await crud_user.get_by_tg_id_or_create(db=db, tg_id=tg_id)

            # 2 Create an invoice with PAID status for new user
            if user:
                invoice_inst = Invoice(user=user.as_dict(),
                                       practise_id=practise_id,
                                       lesson=None,
                                       message=None,
                                       is_online=False,
                                       ticket_count=1
                                       )
                result = await invoice_inst.create_invoice_full_practise_paid(amount=payment_info.total_amount,
                                                                              invoice_id=invoice_uuid,
                                                                              valid_to=PRACTISE_VALID_TO,
                                                                              status='PAID')
                if result:
                    practise = await crud_practise.get(db, id=practise_id)
                    if practise:
                        await message.answer(text=text_decorator.strong(f"Вы успешно оплатили практику: {practise.title}.\n"
                                                                        f"Теперь Вы можете перейти в закрытый канал и увидеть все уроки: "
                                                                        f"{practise.channel_resource_link}\n"
                                                                        "Спасибо, что поддерживаете меня!"))
                else:
                    await message.answer(
                        text=text_decorator.strong(f'Мы не смогли завершить платеж корректно, но не переживайте, '
                                                   'мы получили платеж и сможем Вам помочь. '
                                                   f'Напишите нам сообщение о проблеме и укажите этот номер: {invoice_uuid}')
                    )

                    await user_message_handler(message, state)

    else:
        invoice_uuid = res[0]
        async with SessionLocalAsync() as db:
            invoice_db = await crud_invoice.get_invoice_by_uuid(db, uuid=invoice_uuid)
            if invoice_db:
                invoice_db.status = 'PAID'
                db.add(invoice_db)
                await db.commit()
                await db.refresh(invoice_db)
                await log_message.add_message(
                    await message.answer(text=text_decorator.strong(LEXICON_DEFAULT_NAMES_RU['payment_success']))
                )
                if invoice_db.category == PractiseCategories.ONLINE.value:
                    data = await state.get_data()
                    current_lesson = data.get("view_lesson", None)
                    if current_lesson is not None:
                        await join_online_lesson(message, state)
                    else:
                        await home(message, state, user)
                else:
                    await view_lesson(message, state)
            else:
                await message.answer(
                    text=text_decorator.strong(f'Мы не смогли завершить платеж корректно, но не переживайте, '
                                               'мы получили платеж и сможем Вам помочь. '
                                               f'Напишите нам сообщение о проблеме и укажите этот номер: {invoice_uuid}')
                )

                await user_message_handler(message, state)
