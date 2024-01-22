from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_media, crud_invoice
from db.session import SessionLocalAsync
from keyboards.inline.view_media_menu import MediaMenuKeyboard
from lexicon.lexicon_ru import LEXICON_CHAPTER_LABELS_RU, LEXICON_DEFAULT_NAMES_RU
from states.admin import MediaMenu
from utils import log_message, text_decorator
from utils.constants import MessageTypes
from utils.handler import prepare_context
from utils.invoice import Invoice

# Сколько месяцев открыт доступ к платному контенту
VALID_TO = 3


async def view_lesson(callback: CallbackQuery | Message, state: FSMContext) -> None:
    data = await state.get_data()
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        lesson_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        data = await state.get_data()
        lesson_dict = data.get("view_practise", None)
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
            if not lesson.is_free:
                # Урок ПЛАТНЫЙ!
                async with SessionLocalAsync() as db:
                    invoice = await crud_invoice.get_paid_invoice(db,
                                                                  practise_id=data["view_practise"]["id"],
                                                                  media_id=lesson.id)
                    if invoice:
                        await show_lesson(msg, lesson.as_dict(), valid_to=invoice.valid_to)
                    else:
                        # Урок не оплачен
                        await request_payment(msg, lesson.as_dict(), menu)
            else:
                await show_lesson(msg, lesson.as_dict(), valid_to=None)

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
                text="\nУрок доступен до: " + text_decorator.italic(text_decorator.not_empty(valid_to.strftime("%d-%m-%Y")))
            )
        )

    await _show_free_part(message, lesson)

    match lesson.get("media_type", MessageTypes.NOT_DEFINED.value):
        case MessageTypes.PHOTO.value:
            await log_message.add_message(await message.answer_photo(lesson["free_content_file_id"]))
        case MessageTypes.VIDEO.value:
            await log_message.add_message(await message.answer_video(lesson["free_content_file_id"]))
