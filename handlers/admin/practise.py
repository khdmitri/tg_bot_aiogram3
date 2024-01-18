import traceback
from typing import Optional, List

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_practise
from db.session import SessionLocalAsync
from keyboards.inline import practise_menu_keyboard
from keyboards.inline.practise_menu import PractiseStartMenuKeyboard
from lexicon.lexicon_ru import LEXICON_BTN_GROUP_LABELS_RU, LEXICON_CHAPTER_LABELS_RU, LEXICON_DEFAULT_NAMES_RU
from models.practise import Practise
from schemas.practise import PractiseCreate, PractiseUpdate
from states.admin import PractiseMenu
from utils import message_logger, log_message, text_decorator


async def manage_practises(callback: CallbackQuery, state: FSMContext) -> None:
    # Изменяем состояние на home
    await state.set_state(PractiseMenu.home)
    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(callback.message.chat.id, callback.message)

    await log_message.add_message(await callback.message.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['manage_practise']))
                                  )

    # Получаем список практик с их order, name, type
    async with SessionLocalAsync() as db:
        practises: Optional[List[Practise]] = await crud_practise.get_practises_by_order(db)
        if practises:
            # Формируем inline keyboard
            keyboards = PractiseStartMenuKeyboard(practises=practises)
            await log_message.add_message(await callback.message.answer(
                text=LEXICON_BTN_GROUP_LABELS_RU['practise_list'],
                reply_markup=keyboards.get_keyboard()
            ))
        else:
            keyboards = PractiseStartMenuKeyboard()

    # Показываем дополнительное меню
    await log_message.add_message(await callback.message.answer(
        text=LEXICON_BTN_GROUP_LABELS_RU['practise_actions'],
        reply_markup=keyboards.get_extra_keyboard() if keyboards else None
    ))


async def add_practise(callback: CallbackQuery, state: FSMContext) -> None:
    # Меняем состояние на новая практика
    await state.set_state(PractiseMenu.new_practise)
    # Создаем новую практику
    async with SessionLocalAsync() as db:
        new_practise = {
            "order": await crud_practise.get_last_order(db),
            "title": LEXICON_DEFAULT_NAMES_RU['practise_title'],
            "description": LEXICON_DEFAULT_NAMES_RU['practise_description'],
            "media_file_id": None,
            "media_type": None,
            "thumbs": None,
        }
        new_practise = PractiseCreate(**new_practise)
        await crud_practise.create(db, obj_in=new_practise)

    # Вызываем хэндлер для управления практиками
    await manage_practises(callback, state)


async def edit_practise(callback: CallbackQuery | Message, state: FSMContext) -> None:
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        practise_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        data = await state.get_data()
        practise_dict = data.get("edit_practise", None)
        practise_id = practise_dict["id"]

    # Изменяем состояние на home
    await state.set_state(PractiseMenu.edit)
    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(msg.chat.id, msg)
    # Пишем название раздела
    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['edit_practise']))
                                  )
    async with SessionLocalAsync() as db:
        practise = await crud_practise.get(db, id=practise_id)
        if practise:
            await state.update_data(edit_practise=practise.as_dict())
            await show_practise(msg, practise.as_dict())


async def show_practise(message: Message, practise: dict):
    await log_message.add_message(await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['title'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(practise.get("title", "")),
        reply_markup=practise_menu_keyboard.get_change_title_keyboard()
    ))

    await log_message.add_message(await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['description'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(practise.get("description", "")),
        reply_markup=practise_menu_keyboard.get_change_description_keyboard()
    ))

    await log_message.add_message(await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['media_content'])))
    match practise.get("media_type", ""):
        case "photo":
            await log_message.add_message(await message.answer_photo(
                practise["media_file_id"],
                reply_markup=practise_menu_keyboard.get_change_media_keyboard()))
        case "photo":
            await log_message.add_message(await message.answer_video(
                practise["media_file_id"],
                reply_markup=practise_menu_keyboard.get_change_media_keyboard()))
        case _:
            await log_message.add_message(await message.answer(
                text=LEXICON_DEFAULT_NAMES_RU['media_content_empty'],
                reply_markup=practise_menu_keyboard.get_change_media_keyboard()
            ))

    await log_message.add_message(await message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
        reply_markup=practise_menu_keyboard.get_back_to_list_keyboard()
    ))


async def practise_change_title_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    # Изменяем состояние на home
    await state.set_state(PractiseMenu.change_title)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_change_title'],
        reply_markup=practise_menu_keyboard.get_cancel_change_keyboard()
    ))))


async def practise_change_title_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    practise_dict = data.get("edit_practise", None)
    practise_dict["title"] = message.text
    await update_practise(practise_dict, message, state)


async def practise_change_description_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    # Изменяем состояние на home
    await state.set_state(PractiseMenu.change_description)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_change_decription'],
        reply_markup=practise_menu_keyboard.get_cancel_change_keyboard()
    ))))


async def practise_change_description_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    practise_dict = data.get("edit_practise", None)
    practise_dict["description"] = message.text
    await update_practise(practise_dict, message, state)


async def practise_change_media_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    # Изменяем состояние на home
    await state.set_state(PractiseMenu.change_description)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_change_media'],
        reply_markup=practise_menu_keyboard.get_cancel_change_keyboard()
    ))))


async def practise_change_media_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    practise_dict = data.get("edit_practise", None)
    if message.video:
        practise_dict['media_type'] = "video"
        practise_dict['media_file_id'] = message.video.file_id
    elif message.photo:
        practise_dict['media_type'] = "photo"
        practise_dict['media_file_id'] = message.photo[-1].file_id
        practise_dict['thumbs'] = message.photo[-1].file_id
    await update_practise(practise_dict, message, state)


async def update_practise(practise_dict: dict, message: Message, state: FSMContext):
    await state.update_data(edit_practise=practise_dict)
    if practise_dict is not None:
        async with SessionLocalAsync() as db:
            try:
                practise_db = await crud_practise.get(db, id=practise_dict["id"])
                update_practise_schema = PractiseUpdate(**practise_dict)
                if practise_db:
                    await crud_practise.update(db, db_obj=practise_db, obj_in=update_practise_schema)
            except Exception:
                print(traceback.format_exc())

    # Изменяем состояние на home
    await state.set_state(PractiseMenu.edit)
    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(message.chat.id, message)
    await show_practise(message, practise_dict)


async def delete_practise(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    practise_dict = data.get('edit_practise', None)
    if practise_dict is not None:
        async with SessionLocalAsync() as db:
            try:
                await crud_practise.remove(db, id=practise_dict['id'])
            except Exception:
                print(traceback.format_exc())

    await callback.answer(LEXICON_DEFAULT_NAMES_RU['delete_success'])
    await manage_practises(callback, state)


async def cancel_change(message: Message, state: FSMContext) -> None:
    # Изменяем состояние на home
    await state.set_state(PractiseMenu.edit)
    await edit_practise(message, state)
