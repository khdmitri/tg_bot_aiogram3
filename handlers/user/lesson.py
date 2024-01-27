from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_media, crud_invoice, crud_group, crud_user
from db.session import SessionLocalAsync
from keyboards.inline.view_media_menu import MediaMenuKeyboard
from lexicon.lexicon_ru import LEXICON_CHAPTER_LABELS_RU, LEXICON_DEFAULT_NAMES_RU
from models.group import Group
from models.media import Media
from schemas import GroupCreate
from states.admin import MediaMenu
from utils import log_message, text_decorator
from utils.constants import MessageTypes, PractiseCategories
from utils.handler import prepare_context, if_user_is_group_member
from utils.invoice import Invoice

# Сколько месяцев открыт доступ к платному контенту
VALID_TO = 3

# Количество уроков в абонементе
ONLINE_LESSON_NUMBER = 10


async def process_lesson(*, message: Message, lesson: Media, data: dict, menu: MediaMenuKeyboard):
    if not lesson.is_free:
        # Урок ПЛАТНЫЙ!
        async with SessionLocalAsync() as db:
            invoice = await crud_invoice.get_paid_invoice(db,
                                                          practise_id=data["view_practise"]["id"],
                                                          media_id=lesson.id)
            if invoice:
                await show_lesson(message, lesson.as_dict(), valid_to=invoice.valid_to)
            else:
                # Урок не оплачен
                await request_payment(message, lesson.as_dict(), menu)
    else:
        await show_lesson(message, lesson.as_dict(), valid_to=None)


async def add_member_to_group(message: Message, lesson: dict, user: dict, menu: MediaMenuKeyboard):
    async with SessionLocalAsync() as db:
        group_schema = GroupCreate(**{
            "user_id": user["id"],
            "media_id": lesson["id"]
        })
        await crud_group.create(db, obj_in=group_schema)
        m = [
            f'Вы успешно записаны на online-занятие!',
            f'Online занятие по йоге состоится: {datetime.fromtimestamp(lesson["action_date"]).strftime("%d.%m.%Y %H:%M")}, ВРЕМЯ МОСКОВСКОЕ (GMT+3)',
            f'Тема занятия: {lesson["title"]}',
            f'Для участия перейдите по ссылке на стрим: <a>{lesson["stream_link"]}</a>' if lesson["stream_link"] else
            'Ссылка на стрим будет отправлена Вам дополнительно',
        ]
        await log_message.add_message(await message.answer(text="\n".join(m)))
        await log_message.add_message(await message.answer(
            text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
            reply_markup=menu.get_back_previous()
        ))


async def online_pay_action(callback: CallbackQuery, state: FSMContext, user: dict):
    data = await state.get_data()
    await state.update_data(user=user)
    invoice_inst = Invoice(user=user,
                           practise_id=data["view_practise"]["id"],
                           lesson=data["view_lesson"],
                           message=callback.message,
                           is_online=True,
                           ticket_count=1
                           )
    await invoice_inst.send_invoice()


async def online_abonement_pay_action(callback: CallbackQuery, state: FSMContext, user: dict):
    data = await state.get_data()
    await state.update_data(user=user)
    invoice_inst = Invoice(user=user,
                           practise_id=data["view_practise"]["id"],
                           lesson=data["view_lesson"],
                           message=callback.message,
                           is_online=True,
                           ticket_count=ONLINE_LESSON_NUMBER
                           )
    await invoice_inst.send_invoice()


async def lesson_checkout_action(callback: CallbackQuery, state: FSMContext, user):
    data = await state.get_data()
    lesson = data["view_lesson"]
    async with SessionLocalAsync() as db:
        if not lesson["is_free"]:
            invoice = await crud_invoice.get_online_invoice(db, user["id"])
            if invoice:
                invoice.ticket_count += 1
                db.add(invoice)
                await db.commit()
                await db.refresh(invoice)
        member: Group = await crud_group.is_member(db, user_id=user["id"], media_id=lesson["id"])
        if member:
            await crud_group.remove(db, id=member.id)
    await view_lesson(callback.message, state)


async def join_online_lesson(callback: CallbackQuery | Message, state: FSMContext):
    await state.set_state(MediaMenu.join_online_lesson)
    msg = callback.message if isinstance(callback, CallbackQuery) else callback
    data = await state.get_data()
    if data.get("user", None) is None and isinstance(callback, CallbackQuery):
        async with SessionLocalAsync() as db:
            user_db = await crud_user.get_by_tg_id(db, callback.from_user.id)
            await state.update_data(user=user_db.as_dict())
            user = user_db.as_dict()
    else:
        user = data["user"]
    await prepare_context(state, MediaMenu.join_online_lesson, msg)
    data = await state.get_data()
    lesson = data["view_lesson"]
    menu = MediaMenuKeyboard(practise_id=data['view_practise']['id'])

    # Случай, когда пользователь УЖЕ записался на занятие
    async with SessionLocalAsync() as db:
        if await if_user_is_group_member(db, user_id=user["id"], media_id=lesson["id"]):
            await log_message.add_message(await msg.answer(
                text=LEXICON_DEFAULT_NAMES_RU['already_in_group'],
                reply_markup=menu.get_checkout_keyboard()
            ))
        else:

            # Если урок бесплатный, просто записываем в группу, если платный, проверяем, была ли оплата
            if lesson["is_free"]:
                await add_member_to_group(msg, lesson, user, menu)
            else:
                async with SessionLocalAsync() as db:
                    invoice = await crud_invoice.get_valid_online_invoice(db, user_id=user["id"])
                    if invoice:
                        await add_member_to_group(msg, lesson, user, menu)
                        invoice.ticket_count -= 1
                        db.add(invoice)
                        await db.commit()
                        await db.refresh(invoice)
                        m = [
                            '☯☯☯ Вы были успешно записаны на ONLINE-занятие!',
                            'На Вашем абонементе осталось доступных поcещений: ' +
                            text_decorator.strong(str(invoice.ticket_count))
                        ]
                        await log_message.add_message(await msg.answer(
                            text="\n".join(m)
                        ))
                    else:
                        await log_message.add_message(await msg.answer(
                            text=LEXICON_DEFAULT_NAMES_RU['lesson_online_payment_menu'],
                            reply_markup=menu.get_payment_online_keyboard()
                        ))


async def process_online_lesson(*, message: Message, state: FSMContext, lesson: Media, menu: MediaMenuKeyboard):
    await show_lesson(message, lesson.as_dict(), valid_to=lesson.action_date)

    if lesson.is_free:
        await log_message.add_message(await message.answer(
            text=LEXICON_DEFAULT_NAMES_RU['free_online_lesson'])
                                      )
    else:
        m = [
            '☯☯☯☯☯☯☯☯☯☯☯☯☯',
            LEXICON_DEFAULT_NAMES_RU['comm_online_lesson'],
            text_decorator.strong(LEXICON_DEFAULT_NAMES_RU['payment_cost'] + str(lesson.cost) + ' руб.'),
            '☯☯☯☯☯☯☯☯☯☯☯☯☯'
        ]
        await log_message.add_message(await message.answer(text="\n".join(m)))

    # Кнопка "Записаться на онлайн урок"
    await log_message.add_message(await message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['online_join_menu'],
        reply_markup=menu.get_join_keyboard()
    ))


async def view_lesson(callback: CallbackQuery | Message, state: FSMContext) -> None:
    data = await state.get_data()
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        lesson_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        data = await state.get_data()
        lesson_dict = data.get("view_lesson", None)
        lesson_id = lesson_dict["id"]

    menu = MediaMenuKeyboard(practise_id=data['view_practise']['id'])
    await prepare_context(state, MediaMenu.view, msg)
    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['view_lesson_selected']))
                                  )

    async with SessionLocalAsync() as db:
        lesson = await crud_media.get(db, id=lesson_id)
        if lesson:
            await state.update_data(view_lesson=lesson.as_dict())
            if data["view_practise"].get("category",
                                         PractiseCategories.LESSON.value) == PractiseCategories.ONLINE.value:
                await process_online_lesson(message=msg, state=state, lesson=lesson, menu=menu)
            else:
                await process_lesson(message=msg, lesson=lesson, data=data, menu=menu)

    await log_message.add_message(await msg.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
        reply_markup=menu.get_back_previous()
    ))


async def _show_free_part(message: Message, lesson: dict):
    await log_message.add_message(
        await message.answer(
            text="\nУРОВЕНЬ ПОДГОТОВКИ: " + text_decorator.italic(text_decorator.not_empty(lesson.get("category", "")))
        )
    )

    await log_message.add_message(
        await message.answer(text=text_decorator.not_empty(text_decorator.strong(lesson["title"])))
    )

    await log_message.add_message(
        await message.answer(text=text_decorator.not_empty(lesson["description"]))
    )


async def request_payment(message: Message, lesson: dict, menu: MediaMenuKeyboard):
    await _show_free_part(message, lesson)
    await log_message.add_message(
        await message.answer(
            text=LEXICON_DEFAULT_NAMES_RU['invite_payment'],
        )
    )
    await log_message.add_message(
        await message.answer(
            text=LEXICON_DEFAULT_NAMES_RU['payment_cost'] + str(lesson["cost"]) + "руб.",
            reply_markup=menu.get_payment_keyboard()
        )
    )


async def lesson_pay_action(callback: CallbackQuery, state: FSMContext, user: dict):
    data = await state.get_data()
    invoice_inst = Invoice(user=user,
                           practise_id=data["view_practise"]["id"],
                           lesson=data["view_lesson"],
                           message=callback.message
                           )
    await invoice_inst.send_invoice(valid_to=VALID_TO)


async def show_lesson(message: Message, lesson: dict, valid_to: datetime | None):
    if valid_to is not None:
        await log_message.add_message(
            await message.answer(
                text="\nУрок доступен до: " + text_decorator.italic(
                    text_decorator.not_empty(valid_to.strftime("%d-%m-%Y")))
            )
        )

    await _show_free_part(message, lesson)

    match lesson.get("media_type", MessageTypes.NOT_DEFINED.value):
        case MessageTypes.PHOTO.value:
            await log_message.add_message(await message.answer_photo(lesson["free_content_file_id"]))
        case MessageTypes.VIDEO.value:
            await log_message.add_message(await message.answer_video(lesson["free_content_file_id"]))
