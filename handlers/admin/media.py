import traceback
from datetime import datetime, timedelta

import pytz
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_media, crud_media_group, crud_group, crud_invoice
from data import config
from db.session import SessionLocalAsync
from handlers.admin.practise import edit_practise
from keyboards.inline.media_menu import MediaMenuKeyboard
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU, LEXICON_CHAPTER_LABELS_RU, LEXICON_MEDIA_CATEGORIES_RU
from middlewares import message_logger
from schemas import MediaGroupCreate
from schemas.media import MediaCreate, MediaUpdate
from states.admin import MediaMenu
from utils import log_message, text_decorator
from utils.constants import MessageTypes, PractiseCategories
from utils.db_utils import swap_orders
from utils.handler import prepare_media_group, prepare_context


async def add_media(callback: CallbackQuery | Message, state: FSMContext) -> None:
    # Меняем состояние на новый урок
    await state.set_state(MediaMenu.new)
    # Ищем практику, для которой добавляется урок
    data = await state.get_data()
    practise = data['edit_practise']
    match practise.get("category", PractiseCategories.LESSON.value):
        case PractiseCategories.ONLINE.value:
            action_date = datetime.now() + timedelta(days=2)
            is_free = False
            cost = config.DEFAULT_ONLINE_COST
        case _:
            action_date = None
            is_free = True
            cost = 0
    # Создаем новый урок
    async with SessionLocalAsync() as db:
        new_media = {
            "practise_id": practise["id"],
            "order": await crud_media.get_last_order(db),
            "title": LEXICON_DEFAULT_NAMES_RU['media_title'],
            "is_free": is_free,
            "description": LEXICON_DEFAULT_NAMES_RU['media_description'],
            "free_content_file_id": None,
            "comm_content_file_id": None,
            "cost": cost,
            "media_type": MessageTypes.NOT_DEFINED.value,
            "category": LEXICON_MEDIA_CATEGORIES_RU['any'],
            "ticket_count": 1,
            "action_date": action_date,
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


async def edit_online_media(callback: CallbackQuery | Message, state: FSMContext) -> None:
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        media_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        data = await state.get_data()
        media_dict = data.get("edit_media", None)
        media_id = media_dict["id"]

    await prepare_context(state, MediaMenu.edit, message=callback.message)

    # Пишем название раздела
    await log_message.add_message(await msg.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['edit_online_media']))
                                  )
    async with SessionLocalAsync() as db:
        media = await crud_media.get(db, id=media_id)
        if media:
            await state.update_data(edit_media=media.as_dict())
            await show_online_media(msg, media.as_dict(), state)


async def spam_stream_link(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    media = data["edit_media"]
    bot = callback.bot

    m = [
        f'Online занятие по йоге состоится: {datetime.fromtimestamp(media["action_date"]).strftime("%d.%m.%Y %H:%M")}, ВРЕМЯ МОСКОВСКОЕ (GMT+3)',
        f'Тема занятия: {media["title"]}',
        f'Для участия перейдите по ссылке на стрим: <a>{media["stream_link"]}</a>',
    ]

    async with SessionLocalAsync() as db:
        group = await crud_group.get_group_by_media_id(db, media_id=media["id"])
        for member in group:
            await log_message.add_message(
                await bot.send_message(member.user.tg_id, text="\n".join(m))
            )

    await callback.answer(text="Сообщение успешно отправлено всем участникам группы!", show_alert=True)


async def show_online_media(message: Message, media: dict, state: FSMContext):
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

    await log_message.add_message(
        await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['stream_link'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text_decorator.not_empty(media.get("stream_link", "-"))),
        reply_markup=media_menu_keyboard.get_change_stream_link_keyboard()
    ))

    # Если стрим линк активирован, надо положить кнопку - Отоправить всем, кто в группе
    if media.get("stream_link", None) is not None:
        await log_message.add_message(await message.answer(
            text=text_decorator.strong(LEXICON_DEFAULT_NAMES_RU['spam_stream_link']),
            reply_markup=media_menu_keyboard.get_spam_stream_link_keyboard()
        ))

    await log_message.add_message(await message.answer(
        text=text_decorator.strong(text),
        reply_markup=media_menu_keyboard.get_change_free_keyboard()
    ))

    action_date = media.get("action_date", None)
    if action_date:
        action_date = datetime.fromtimestamp(action_date).strftime("%d.%m.%y %H:%M")
    else:
        action_date = "-"

    await log_message.add_message(
        await message.answer(text=text_decorator.italic(LEXICON_DEFAULT_NAMES_RU['media_action_date'])))
    await log_message.add_message(await message.answer(
        text=text_decorator.strong(action_date),
        reply_markup=media_menu_keyboard.get_change_action_date_keyboard()
    ))

    await log_message.add_message(await message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
        reply_markup=media_menu_keyboard.get_back_previous()
    ))


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


async def media_change_action_date_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MediaMenu.change_action_date)
    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['media_change_action_date'],
        reply_markup=(await _get_media_menu_keyboard(state)).get_cancel_change_keyboard()
    ))))


async def media_change_action_date_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)
    try:
        media_dict["action_date"] = datetime.timestamp(datetime.strptime(message.text, '%d.%m.%Y %H:%M'))
        await update_media(media_dict, message, state)
    except ValueError:
        await log_message.add_message(
            await message.answer(text="Дата в неверном формате, должно быть день.месяц.год(4) часы:минуты")
        )


async def media_change_stream_link_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MediaMenu.change_stream_link)
    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['media_change_stream_link'],
        reply_markup=(await _get_media_menu_keyboard(state)).get_cancel_change_keyboard()
    ))))


async def media_change_stream_link_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_dict = data.get("edit_media", None)
    media_dict["stream_link"] = message.text
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
                media_dict_copy = media_dict.copy()
                if media_dict.get("action_date", None):
                    media_dict_copy["action_date"] = datetime.fromtimestamp(media_dict["action_date"])
                update_media_schema = MediaUpdate(**media_dict_copy)
                if media_db:
                    await crud_media.update(db, db_obj=media_db, obj_in=update_media_schema)
            except Exception:
                print(traceback.format_exc())

    await prepare_context(state, MediaMenu.edit, message)
    data = await state.get_data()
    practise = data.get("edit_practise")
    if practise.get("category", PractiseCategories.LESSON.value) == PractiseCategories.ONLINE.value:
        await show_online_media(message, media_dict, state)
    else:
        await show_media(message, media_dict, state)


async def delete_media(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    media_dict = data.get('edit_media', None)
    practise_dict = data.get('edit_practise', None)
    if practise_dict["category"] == PractiseCategories.ONLINE.value:
        async with SessionLocalAsync() as db:
            members = await crud_group.get_group_by_media_id(db, media_id=media_dict["id"])
            for member in members:
                m = [
                    f'Уважаемый, {member.user.fullname}!',
                    f'Приносим свои извинения за отмену ONLINE-занятия,',
                    f'которое должно было состояться {datetime.fromtimestamp(media_dict["action_date"])}',
                ]
                if not media_dict["is_free"]:
                    m.append('Ваша оплата была добавлена к личному абонементу на любое платное ONLINE-занятие.')
                invoice = await crud_invoice.get_online_invoice(db, user_id=member.user_id)
                if invoice and invoice.status in ["PAID", ]:
                    invoice.ticket_count += 1
                    db.add(invoice)
                    await db.commit()
                    await db.refresh(invoice)
                await log_message.add_message(await callback.bot.send_message(member.user.tg_id, text="\n".join(m)))
                await crud_group.remove(db, id=member.id)
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
