import traceback

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_media, crud_media_group
from db.session import SessionLocalAsync
from handlers.admin.practise import edit_practise
from keyboards.inline.media_menu import MediaMenuKeyboard
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU, LEXICON_CHAPTER_LABELS_RU, LEXICON_MEDIA_CATEGORIES_RU
from middlewares import message_logger
from schemas import MediaGroupCreate
from schemas.media import MediaCreate, MediaUpdate
from states.admin import MediaMenu
from utils import log_message, text_decorator
from utils.constants import MessageTypes
from utils.db_utils import swap_orders
from utils.handler import prepare_media_group


async def add_media(callback: CallbackQuery | Message, state: FSMContext) -> None:
    # Меняем состояние на новый урок
    await state.set_state(MediaMenu.new)
    # Ищем практику, для которой добавляется урок
    data = await state.get_data()
    practise = data['edit_practise']
    # Создаем новый урок
    async with SessionLocalAsync() as db:
        new_media = {
            "practise_id": practise["id"],
            "order": await crud_media.get_last_order(db),
            "title": LEXICON_DEFAULT_NAMES_RU['media_title'],
            "is_free": True,
            "description": LEXICON_DEFAULT_NAMES_RU['media_description'],
            "free_content_file_id": None,
            "comm_content_file_id": None,
            "cost": 0,
            "media_type": MessageTypes.NOT_DEFINED.value,
            "category": LEXICON_MEDIA_CATEGORIES_RU['any'],
        }
        new_media = MediaCreate(**new_media)
        await crud_media.create(db, obj_in=new_media)

    # Вызываем хэндлер для управления практиками
    await edit_practise(callback.message, state)


async def edit_media(callback: CallbackQuery | Message, state: FSMContext) -> None:
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        media_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        data = await state.get_data()
        media_dict = data.get("edit_media", None)
        media_id = media_dict["id"]

    # Изменяем состояние на home
    await state.set_state(MediaMenu.edit)
    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(msg.chat.id, msg)
    # Пишем название раздела
    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['edit_media']))
                                  )
    async with SessionLocalAsync() as db:
        media = await crud_media.get(db, id=media_id)
        if media:
            await state.update_data(edit_media=media.as_dict())
            await show_media(msg, media.as_dict(), state)


async def show_media(message: Message, media: dict, state: FSMContext):
    data = await state.get_data()

    media_menu_keyboard = MediaMenuKeyboard(practise_id=data["edit_practise"]["id"])
    await log_message.add_message(await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['title'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text_decorator.not_empty(media.get("title", "-"))),
        reply_markup=media_menu_keyboard.get_change_title_keyboard()
    ))

    await log_message.add_message(
        await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['media_category'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text_decorator.not_empty(media.get("category", "-"))),
        reply_markup=media_menu_keyboard.get_change_category_keyboard()
    ))

    await log_message.add_message(
        await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['description'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text_decorator.not_empty(media.get("description", "-"))),
        reply_markup=media_menu_keyboard.get_change_description_keyboard()
    ))

    await log_message.add_message(
        await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['media_content'])))
    match media.get("media_type", MessageTypes.NOT_DEFINED.value):
        case MessageTypes.PHOTO.value:
            await log_message.add_message(await message.answer_photo(
                media["free_content_file_id"],
                reply_markup=media_menu_keyboard.get_change_media_keyboard()))
        case MessageTypes.VIDEO.value:
            await log_message.add_message(await message.answer_video(
                media["free_content_file_id"],
                reply_markup=media_menu_keyboard.get_change_media_keyboard()))
        case MessageTypes.MEDIA_GROUP.value:
            await log_message.add_message(await message.answer_media_group(
                media=await prepare_media_group(media["media_group_id"]),
                reply_markup=media_menu_keyboard.get_change_media_keyboard())
            )
        case MessageTypes.NOT_DEFINED.value:
            await log_message.add_message(await message.answer(
                text=LEXICON_DEFAULT_NAMES_RU['media_content_empty'],
                reply_markup=media_menu_keyboard.get_change_media_keyboard()
            ))

    if media["is_free"]:
        text = LEXICON_DEFAULT_NAMES_RU['media_content_free']
    else:
        text = LEXICON_DEFAULT_NAMES_RU['media_content_not_free']
        await log_message.add_message(
            await message.answer(
                text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['media_cost']) + ': ' + str(media.get("cost", 0)) + 'руб',
                reply_markup=media_menu_keyboard.get_change_cost_keyboard()
            )
        )

    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text),
        reply_markup=media_menu_keyboard.get_change_free_keyboard()
    ))

    await log_message.add_message(await message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
        reply_markup=media_menu_keyboard.get_back_previous()
    ))


async def media_change_free_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)

    media_dict['is_free'] = not media_dict['is_free']

    await update_media(media_dict, callback.message, state)


async def _get_media_menu_keyboard(state: FSMContext) -> MediaMenuKeyboard:
    data = await state.get_data()
    practise = data.get("edit_practise", None)
    return MediaMenuKeyboard(practise_id=practise["id"])


async def media_change_category_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MediaMenu.change_category)
    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['media_change_category'],
        reply_markup=(await _get_media_menu_keyboard(state)).get_category_keyboard()
    ))))


async def media_change_category_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)
    media_dict["category"] = message.text
    await update_media(media_dict, message, state)


async def media_change_title_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MediaMenu.change_title)
    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['media_change_title'],
        reply_markup=(await _get_media_menu_keyboard(state)).get_cancel_change_keyboard()
    ))))


async def media_change_title_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)
    media_dict["title"] = message.text
    await update_media(media_dict, message, state)


async def media_change_cost_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MediaMenu.change_cost)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['media_change_cost'],
        reply_markup=(await _get_media_menu_keyboard(state)).get_cancel_change_keyboard()
    ))))


async def media_change_cost_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)
    media_dict["cost"] = int(message.text)
    await update_media(media_dict, message, state)


async def media_change_description_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MediaMenu.change_description)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['media_change_description'],
        reply_markup=(await _get_media_menu_keyboard(state)).get_cancel_change_keyboard()
    ))))


async def media_change_description_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)
    media_dict["description"] = message.text
    await update_media(media_dict, message, state)


async def media_change_media_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MediaMenu.change_media)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['media_change_media'],
        reply_markup=(await _get_media_menu_keyboard(state)).get_cancel_change_keyboard()
    ))))


async def media_lessons_swap(callback: CallbackQuery, state: FSMContext) -> None:
    lessons_swap_ids = [int(callback.data.split(":")[1]), int(callback.data.split(":")[2])]
    if lessons_swap_ids[0] > 0:
        async with SessionLocalAsync() as db:
            await swap_orders(db, lessons_swap_ids, crud_media)

    await callback.answer(text=LEXICON_DEFAULT_NAMES_RU['success_swap'])
    await edit_practise(callback.message, state)


async def media_change_media_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)
    if message.media_group_id:
        async with SessionLocalAsync() as db:
            media = await crud_media.update_media_group_id(db, media_dict["id"], int(message.media_group_id))
            media_dict = media.as_dict()
            await state.update_data(edit_post=media_dict)
            media_type = MessageTypes.NOT_DEFINED.value
            media_file_id = ""
            if message.photo:
                media_type = MessageTypes.PHOTO.value
                media_file_id = message.photo[-1].file_id
            elif message.video:
                media_type = MessageTypes.VIDEO.value
                media_file_id = message.video.file_id
            media_group = MediaGroupCreate(media_type=media_type,
                                           media_group_id=int(message.media_group_id),
                                           media_file_id=media_file_id)
            await crud_media_group.create(db, obj_in=media_group)
        await message.delete()
    elif message.video:
        media_dict['media_type'] = MessageTypes.VIDEO.value
        media_dict['free_content_file_id'] = message.video.file_id
    elif message.photo:
        media_dict['media_type'] = MessageTypes.PHOTO.value
        media_dict['free_content_file_id'] = message.photo[-1].file_id
    else:
        media_dict['media_type'] = MessageTypes.TEXT_MESSAGE.value
        media_dict['text'] = message.text
    if message.media_group_id:
        text_decorator.italic(await log_message.add_message(await message.answer(
            text=f"Файл был добавлен в группу."
        )))
    else:
        await update_media(media_dict, message, state)


async def update_media(media_dict: dict, message: Message, state: FSMContext):
    await state.update_data(edit_media=media_dict)
    if media_dict is not None:
        async with SessionLocalAsync() as db:
            try:
                media_db = await crud_media.get(db, id=media_dict["id"])
                update_media_schema = MediaUpdate(**media_dict)
                if media_db:
                    await crud_media.update(db, db_obj=media_db, obj_in=update_media_schema)
            except Exception:
                print(traceback.format_exc())

    # Изменяем состояние на home
    await state.set_state(MediaMenu.edit)
    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(message.chat.id, message)
    await show_media(message, media_dict, state)


async def delete_media(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    media_dict = data.get('edit_media', None)
    if media_dict is not None:
        async with SessionLocalAsync() as db:
            try:
                await crud_media.remove(db, id=media_dict['id'])
            except Exception:
                print(traceback.format_exc())

    await callback.answer(LEXICON_DEFAULT_NAMES_RU['delete_success'])
    await edit_practise(callback.message, state)


async def cancel_change(message: Message, state: FSMContext) -> None:
    # Изменяем состояние на home
    await state.set_state(MediaMenu.edit)
    await edit_media(message, state)
