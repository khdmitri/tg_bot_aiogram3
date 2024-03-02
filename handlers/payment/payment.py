from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import PreCheckoutQuery, Message

from crud import crud_invoice, crud_user, crud_practise, crud_media, crud_group
from db.session import SessionLocalAsync
from handlers.user.core import user_message_handler
from handlers.user.lesson import view_lesson, join_online_lesson
from handlers.user.start import home
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU
from schemas import GroupCreate
from utils import log_message, text_decorator
from utils.constants import PractiseCategories, WEBAPP_ACTIONS
from utils.invoice import Invoice, DEFAULT_ABONEMENT_COUNT

PRACTISE_VALID_TO = 2  # months


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
        action = res[1]
        order_id = int(res[1])
        tg_id = int(res[2])

        # 1 Get User by tg_id or create a new one
        async with SessionLocalAsync() as db:
            user = await crud_user.get_by_tg_id_or_create(db=db, tg_id=tg_id)

            # 2 Create an invoice with PAID status for new user
            if user:
                # 3. Check the action of payment
                match action:
                    case WEBAPP_ACTIONS.buy_practise.value:
                        invoice_inst = Invoice(user=user.as_dict(),
                                               practise_id=order_id,
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
                            practise = await crud_practise.get(db, id=order_id)
                            if practise:
                                await message.answer(
                                    text=text_decorator.strong(f"Вы успешно оплатили практику: {practise.title}.\n"
                                                               f"Теперь Вы можете перейти в закрытый канал и увидеть все уроки: "
                                                               f"{practise.channel_resource_link}\n"
                                                               "Спасибо, что поддерживаете меня!"))
                        else:
                            await message.answer(
                                text=text_decorator.strong(
                                    f'Мы не смогли завершить платеж корректно, но не переживайте, '
                                    'мы получили платеж и сможем Вам помочь. '
                                    f'Напишите нам сообщение о проблеме и укажите этот номер: {invoice_uuid}')
                            )

                            await user_message_handler(message, state)
                    case WEBAPP_ACTIONS.buy_online.value:
                        online_practise = await crud_practise.get_online_practise(db)
                        lesson = await crud_media.get(db, id=order_id)
                        invoice_inst = Invoice(user=user.as_dict(),
                                               practise_id=online_practise.id,
                                               lesson=lesson.as_dict(),
                                               message=None,
                                               is_online=True,
                                               ticket_count=1
                                               )
                        result = await invoice_inst.create_invoice_online_paid(amount=payment_info.total_amount,
                                                                               invoice_id=invoice_uuid,
                                                                               status='PAID')
                        if result:
                            group_schema = GroupCreate(**{
                                "user_id": user.id,
                                "media_id": lesson.id
                            })
                            group = await crud_group.create(db, obj_in=group_schema)
                            m = [
                                f'Вы успешно записаны на online-занятие!',
                                f'Online занятие по йоге состоится: {datetime.fromtimestamp(lesson["action_date"]).strftime("%d.%m.%Y %H:%M")}, ВРЕМЯ МОСКОВСКОЕ (GMT+3)',
                                f'Тема занятия: {lesson["title"]}',
                                f'Для участия перейдите по ссылке на стрим: <a>{lesson["stream_link"]}</a>' if lesson[
                                    "stream_link"] else
                                'Ссылка на стрим будет отправлена Вам дополнительно',
                            ]
                            if group:
                                await message.answer(text=text_decorator.strong("\n".join(m)))
                        else:
                            await message.answer(
                                text=text_decorator.strong(
                                    f'Мы не смогли завершить платеж корректно, но не переживайте, '
                                    'мы получили платеж и сможем Вам помочь. '
                                    f'Напишите нам сообщение о проблеме и укажите этот номер: {invoice_uuid}')
                            )
                            await user_message_handler(message, state)
                    case WEBAPP_ACTIONS.buy_abonement.value:
                        online_practise = await crud_practise.get_online_practise(db)
                        invoice_inst = Invoice(user=user.as_dict(),
                                               practise_id=online_practise.id,
                                               lesson=None,
                                               message=None,
                                               is_online=True,
                                               ticket_count=DEFAULT_ABONEMENT_COUNT
                                               )
                        result = await invoice_inst.create_invoice_online_paid(amount=payment_info.total_amount,
                                                                               invoice_id=invoice_uuid,
                                                                               status='PAID')
                        if result:
                            m = [
                                f'Вы успешно купили абонемент на online-занятия!',
                                f'Посещений online-занятий доступно: {DEFAULT_ABONEMENT_COUNT}',
                            ]
                            await message.answer(text=text_decorator.strong("\n".join(m)))
                        else:
                            await message.answer(
                                text=text_decorator.strong(
                                    f'Мы не смогли завершить платеж корректно, но не переживайте, '
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
