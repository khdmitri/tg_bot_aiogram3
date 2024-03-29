from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_practise, crud_media
from db.session import SessionLocalAsync
from keyboards.inline.view_practise_menu import PractiseLessonMenuKeyboard
from lexicon.lexicon_ru import LEXICON_CHAPTER_LABELS_RU, LEXICON_DEFAULT_NAMES_RU
from states.admin import PractiseMenu
from utils import log_message, text_decorator
from utils.constants import MessageTypes, PractiseCategories
from utils.handler import prepare_context, prepare_media_group


async def view_practise(callback: CallbackQuery | Message, state: FSMContext, user: dict | None) -> None:
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        practise_id = int(callback.data.split(":")[1])
        await state.update_data(user=user)
    else:
        msg = callback
        data = await state.get_data()
        practise_dict = data.get("view_practise", None)
        practise_id = practise_dict["id"]

    await prepare_context(state, PractiseMenu.view, msg)
    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['view_practise_selected']))
                                  )
    async with SessionLocalAsync() as db:
        practise = await crud_practise.get(db, id=practise_id)
        if practise:
            await state.update_data(view_practise=practise.as_dict())
            await show_practise(msg, practise.as_dict())


async def show_practise(message: Message, practise: dict):
    await log_message.add_message(
        await message.answer(text=text_decorator.not_empty(text_decorator.strong(practise["title"])))
    )

    await log_message.add_message(
        await message.answer(text=text_decorator.not_empty(practise["description"]))
    )

    match practise.get("media_type", MessageTypes.NOT_DEFINED.value):
        case MessageTypes.PHOTO.value:
            await log_message.add_message(await message.answer_photo(practise["media_file_id"]))
        case MessageTypes.VIDEO.value:
            await log_message.add_message(await message.answer_video(practise["media_file_id"]))
        case MessageTypes.MEDIA_GROUP.value:
            await log_message.add_message(await message.answer_media_group(
                media=await prepare_media_group(practise["media_group_id"])
            ))

    async with SessionLocalAsync() as db:
        if practise["category"] == PractiseCategories.ONLINE.value:
            lessons = await crud_media.get_online_by_practise_id(db, practise_id=practise['id'])
        else:
            lessons = await crud_media.get_multi_by_practise_id(db, practise_id=practise['id'])
        keyboard = PractiseLessonMenuKeyboard(lessons)
        await log_message.add_message(await message.answer(
            text=text_decorator.strong(LEXICON_DEFAULT_NAMES_RU['lessons']),
            reply_markup=keyboard.get_keyboard()
        ))

    await log_message.add_message(await message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
        reply_markup=keyboard.get_back_to_list_keyboard()
    ))
