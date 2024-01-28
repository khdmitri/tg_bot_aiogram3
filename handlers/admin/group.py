from datetime import datetime
from aiogram import html, types

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from crud import crud_practise, crud_media, crud_group
from db.session import SessionLocalAsync
from keyboards.inline.group_menu import GroupMenuKeyboard, group_menu_keyboard
from keyboards.inline.practise_menu import PractiseLessonMenuKeyboard
from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU
from states.group import GroupMenu
from utils import log_message, text_decorator
from utils.handler import prepare_context


async def show_online_lessons(callback: CallbackQuery | Message, state: FSMContext):
    msg = callback.message if isinstance(callback, CallbackQuery) else callback
    await prepare_context(state, GroupMenu.view_lessons, message=msg)
    async with SessionLocalAsync() as db:
        practise = await crud_practise.get_online_practise(db)
        if practise:
            lessons = await crud_media.get_online_by_practise_id(db, practise_id=practise.id)
            menu = PractiseLessonMenuKeyboard(lessons=lessons, add_extra=False)
            await log_message.add_message(await msg.answer(
                text=LEXICON_DEFAULT_NAMES_RU['admin_lessons_list'],
                reply_markup=menu.get_online_keyboard()
            ))

        await log_message.add_message(await msg.answer(
            text=LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu'],
            reply_markup=group_menu_keyboard.get_nav_keyboard()
        ))


async def view_online_lesson(callback: CallbackQuery | Message, state: FSMContext):
    if isinstance(callback, CallbackQuery):
        msg = callback.message
        lesson_id = int(callback.data.split(":")[1])
    else:
        msg = callback
        data = await state.get_data()
        lesson_dict = data.get("group_lesson", None)
        lesson_id = lesson_dict["id"]

    await prepare_context(state, GroupMenu.view_group, message=msg)

    async with SessionLocalAsync() as db:
        group_lesson = await crud_media.get(db, id=lesson_id)
        await state.update_data(group_lesson=group_lesson.as_dict())

        m = [
            text_decorator.strong('🧘🧘🧘 ONLINE-ЗАНЯТИЕ 🧘🧘🧘'),
            f'ДАТА: {group_lesson.action_date.strftime("%d.%m.%Y %H:%M")}',
            f'НАЗВАНИЕ: {group_lesson.title}',
        ]
        await log_message.add_message(await msg.answer(text="\n".join(m)))
        members = await crud_group.get_group_by_media_id(db, media_id=lesson_id)
        m = [
            '☯☯☯ Состав группы ☯☯☯',
            '-----------------------',
        ]
        for member in members:
            m.append(f'<a href="tg://user?id={member.user.tg_id}">{html.quote(member.user.fullname)}</a>')

        m.append(f'ВСЕГО УЧАСТНИКОВ: {len(members)}')
        m.append('-----------------------')

        await log_message.add_message(await msg.answer(
            text="\n".join(m),
            reply_markup=group_menu_keyboard.get_keyboard()
        ))


async def send_group_message(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(GroupMenu.group_message_prompt)
    text_decorator.strong(text_decorator.italic(await log_message.add_message(await callback.message.answer(
        text=LEXICON_DEFAULT_NAMES_RU['group_prompt_message'],
        reply_markup=group_menu_keyboard.get_cancel_change_keyboard()
    ))))


async def group_send_message_save(message: Message, state: FSMContext) -> None:
    group_lesson = (await state.get_data())["group_lesson"]
    async with SessionLocalAsync() as db:
        members = await crud_group.get_group_by_media_id(db, media_id=group_lesson["id"])
        for member in members:
            await log_message.add_message(await message.bot.send_message(member.user.tg_id, text=message.text))

        await log_message.add_message(await message.answer(
            text=html.italic(html.bold("Ваше сообщение было разослано всем участникам группы!")),
            reply_markup=group_menu_keyboard.get_deep_keyboard()
        ))


