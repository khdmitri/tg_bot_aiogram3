from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_media
from db.session import SessionLocalAsync
from keyboards.inline.view_media_menu import MediaMenuKeyboard
from lexicon.lexicon_ru import LEXICON_CHAPTER_LABELS_RU, LEXICON_DEFAULT_NAMES_RU
from states.admin import MediaMenu
from utils import log_message, text_decorator
from utils.handler import prepare_context


async def view_lesson(callback: CallbackQuery | Message, state: FSMContext) -> None:
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        lesson_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        data = await state.get_data()
        lesson_dict = data.get("view_practise", None)
        lesson_id = lesson_dict["id"]

    await prepare_context(state, MediaMenu.view, msg)
    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['view_lesson_selected']))
                                  )
    async with SessionLocalAsync() as db:
        lesson = await crud_media.get(db, id=lesson_id)
        if lesson:
            await state.update_data(view_lesson=lesson.as_dict())
            await show_lesson(msg, lesson.as_dict(), state)


async def show_lesson(message: Message, lesson: dict, state: FSMContext):
    await log_message.add_message(
        await message.answer(
            text="\nУРОВЕНЬ ПОДГОТОВКИ: "+text_decorator.italic(text_decorator.not_empty(lesson.get("category", "")))
        )
    )

    await log_message.add_message(
        await message.answer(text=text_decorator.not_empty(text_decorator.strong(lesson["title"])))
    )

    await log_message.add_message(
        await message.answer(text=text_decorator.not_empty(lesson["description"]))
    )

    match lesson.get("media_type", ""):
        case "photo":
            await log_message.add_message(await message.answer_photo(lesson["free_content_file_id"]))
        case "video":
            await log_message.add_message(await message.answer_video(lesson["free_content_file_id"]))

    data = await state.get_data()
    menu = MediaMenuKeyboard(practise_id=data['view_practise']['id'])

    await log_message.add_message(await message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
        reply_markup=menu.get_back_previous()
    ))
