import traceback
from typing import Optional, List

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto

from crud import crud_post, crud_media_group
from db.session import SessionLocalAsync
from keyboards.inline.post_menu import PostMenuKeyboard, PostEditMenuKeyboard
from lexicon.lexicon_ru import LEXICON_CHAPTER_LABELS_RU, LEXICON_BTN_GROUP_LABELS_RU, LEXICON_DEFAULT_NAMES_RU
from models.post import Post
from schemas import MediaGroupCreate
from schemas.post import PostCreate, PostUpdate
from states.admin import Page
from utils import log_message, text_decorator
from utils.constants import MessageTypes
from utils.handler import prepare_context, prepare_media_group


async def manage_page(callback: CallbackQuery | Message, state: FSMContext) -> None:
    if isinstance(callback, CallbackQuery):
        page = callback.data.split(":")[1]
        msg = callback.message
    else:
        data = await state.get_data()
        page = data["page"]
        msg = callback
    await prepare_context(state, Page.manage, msg)

    await state.update_data(page=page)

    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['manage_page']))
                                  )
    # Получаем список постов
    async with SessionLocalAsync() as db:
        posts: Optional[List[Post]] = await crud_post.get_posts_by_page(db, page=page)
        keyboards = PostMenuKeyboard(posts=posts)
        if posts:
            # Формируем inline keyboard
            await log_message.add_message(await msg.answer(
                text=LEXICON_BTN_GROUP_LABELS_RU['post_list'],
                reply_markup=keyboards.get_keyboard()
            ))

    # Показываем дополнительное меню
    await log_message.add_message(await msg.answer(
        text=LEXICON_BTN_GROUP_LABELS_RU['post_actions'],
        reply_markup=keyboards.get_extra_keyboard() if keyboards else None
    ))


async def add_post(callback: CallbackQuery, state: FSMContext) -> None:
    # Меняем состояние
    await state.set_state(Page.new)
    # Создаем новый пост

    data = await state.get_data()

    async with SessionLocalAsync() as db:
        new_post = {
            "order": await crud_post.get_last_order(db),
            "name": LEXICON_DEFAULT_NAMES_RU['post_name'],
            "page": data["page"],
            "media_file_id": None,
            "message_type": MessageTypes.NOT_DEFINED.value,
            "text": "",
        }
        new_post = PostCreate(**new_post)
        await crud_post.create(db, obj_in=new_post)

    # Вызываем хэндлер для управления постами
    await manage_page(callback.message, state)


async def edit_post(callback: CallbackQuery | Message, state: FSMContext) -> None:
    data = await state.get_data()
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        post_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        post_dict = data.get("edit_post", None)
        post_id = post_dict["id"]

    await prepare_context(state, Page.edit, msg)
    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['edit_post']))
                                  )
    async with SessionLocalAsync() as db:
        post = await crud_post.get(db, id=post_id)
        if post:
            await state.update_data(edit_post=post.as_dict())
            await show_post(msg, post.as_dict(), data["page"])


async def show_post(message: Message, post: dict, page):
    keyboard = PostEditMenuKeyboard(page=page)
    await log_message.add_message(await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['name'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text_decorator.not_empty(post.get("name", "-"))),
        reply_markup=keyboard.get_change_name_keyboard()
    ))

    await log_message.add_message(await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['order'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text_decorator.not_empty(str(post.get("order", 0)))),
        reply_markup=keyboard.get_change_order_keyboard()
    ))

    await log_message.add_message(await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['media_content'])))
    match post.get("message_type", MessageTypes.NOT_DEFINED.value):
        case MessageTypes.PHOTO.value:
            await log_message.add_message(await message.answer_photo(
                post["media_file_id"],
                reply_markup=keyboard.get_change_post_keyboard()))
        case MessageTypes.VIDEO.value:
            await log_message.add_message(await message.answer_video(
                post["media_file_id"],
                reply_markup=keyboard.get_change_post_keyboard()))
        case MessageTypes.TEXT_MESSAGE.value:
            await log_message.add_message(await message.answer(
                text=post["text"],
                reply_markup=keyboard.get_change_post_keyboard()
            ))
        case MessageTypes.MEDIA_GROUP.value:
            await log_message.add_message(await message.answer_media_group(
                media=await prepare_media_group(post["media_group_id"]),
                reply_markup=keyboard.get_change_post_keyboard()
            ))
        case MessageTypes.NOT_DEFINED.value:
            await log_message.add_message(await message.answer(
                text=LEXICON_DEFAULT_NAMES_RU['media_content_empty'],
                reply_markup=keyboard.get_change_post_keyboard()
            ))

    await log_message.add_message(await message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
        reply_markup=keyboard.get_back_to_list_keyboard()
    ))


async def post_change_name_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = PostEditMenuKeyboard(page=data["page"])
    # Изменяем состояние
    await state.set_state(Page.change_name)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['post_change_name'],
        reply_markup=keyboard.get_cancel_change_keyboard()
    ))))


async def post_change_name_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    post_dict = data.get("edit_post", None)
    post_dict["name"] = message.text
    await update_post(post_dict, message, state)


async def post_change_order_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = PostEditMenuKeyboard(page=data["page"])
    # Изменяем состояние
    await state.set_state(Page.change_order)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['post_change_order'],
        reply_markup=keyboard.get_cancel_change_keyboard()
    ))))


async def post_change_order_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    post_dict = data.get("edit_post", None)
    post_dict["order"] = int(message.text)
    await update_post(post_dict, message, state)


async def update_post(post_dict: dict, message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(edit_post=post_dict)
    if post_dict is not None:
        async with SessionLocalAsync() as db:
            try:
                post_db = await crud_post.get(db, id=post_dict["id"])
                update_post_schema = PostUpdate(**post_dict)
                if post_db:
                    await crud_post.update(db, db_obj=post_db, obj_in=update_post_schema)
            except Exception:
                print(traceback.format_exc())

    await prepare_context(state, Page.edit, message)
    await show_post(message, post_dict, page=data["page"])


async def post_change_post_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = PostEditMenuKeyboard(page=data["page"])
    # Изменяем состояние
    await state.set_state(Page.change_post)

    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['post_change_post'],
        reply_markup=keyboard.get_cancel_change_keyboard()
    ))))


async def post_change_post_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    post_dict = data.get("edit_post", None)
    if message.media_group_id:
        async with SessionLocalAsync() as db:
            post = await crud_post.update_media_group_id(db, post_dict["id"], int(message.media_group_id))
            post_dict = post.as_dict()
            await state.update_data(edit_post=post_dict)
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
        post_dict['message_type'] = MessageTypes.VIDEO.value
        post_dict['media_file_id'] = message.video.file_id
    elif message.photo:
        post_dict['message_type'] = MessageTypes.PHOTO.value
        post_dict['media_file_id'] = message.photo[-1].file_id
    else:
        post_dict['message_type'] = MessageTypes.TEXT_MESSAGE.value
        post_dict['text'] = message.text
    if message.media_group_id:
        text_decorator.italic(await log_message.add_message(await message.answer(
            text=f"Файл был добавлен в группу."
        )))
    else:
        await update_post(post_dict, message, state)


async def delete_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post_dict = data.get('edit_post', None)
    if post_dict is not None:
        async with SessionLocalAsync() as db:
            try:
                await crud_post.remove(db, id=post_dict['id'])
            except Exception:
                print(traceback.format_exc())

    await callback.answer(LEXICON_DEFAULT_NAMES_RU['delete_success'])
    await manage_page(callback.message, state)


async def cancel_change(message: Message, state: FSMContext) -> None:
    # Изменяем состояние
    await state.set_state(Page.edit)
    await edit_post(message, state)
