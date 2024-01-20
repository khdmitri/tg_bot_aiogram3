from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from crud import crud_user, crud_practise
from db.session import SessionLocalAsync
from keyboards.default import BasicButtons
from keyboards.inline.view_practise_menu import ViewPractiseMenuKeyboard
from lexicon.lexicon_ru import LEXICON_CHAPTER_LABELS_RU, LEXICON_DEFAULT_MESSGES_RU, LEXICON_DEFAULT_NAMES_RU
from middlewares import message_logger
from states.user import UserMainMenu
from utils import log_message, text_decorator
from utils.handler import prepare_context


async def view_practises_handler(callback: CallbackQuery, state: FSMContext):
    await prepare_context(state, UserMainMenu.view_practises, callback.message)

    async with SessionLocalAsync() as db:
        practises = await crud_practise.get_practises_by_order(db, only_published=True)
        menu = ViewPractiseMenuKeyboard(practises)

        # Пишем название раздела
        await log_message.add_message(await callback.message.answer(
            text=text_decorator.strong(
                LEXICON_CHAPTER_LABELS_RU['view_practises']),
            reply_markup=menu.get_keyboard()
        ))

    await log_message.add_message(await callback.message.answer(
        text=text_decorator.strong(
            LEXICON_DEFAULT_NAMES_RU['practise_navigation_menu']),
        reply_markup=menu.get_extra_keyboard()
    ))


async def user_message_handler(callback: CallbackQuery, state: FSMContext):
    await prepare_context(state, UserMainMenu.message, callback.message)

    # Пишем название раздела
    await log_message.add_message(await callback.message.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['user_message']),
        reply_markup=BasicButtons.back()
    ))
    await callback.answer(text=LEXICON_DEFAULT_MESSGES_RU['message_sent'])


async def forward_message_handler(message: Message, state: FSMContext):
    async with SessionLocalAsync() as db:
        admins = await crud_user.get_admins(db)
        bot = message.bot
        for admin in admins:
            await bot.forward_message(admin.tg_id, message_id=message.message_id, from_chat_id=message.chat.id)
