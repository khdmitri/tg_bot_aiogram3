from aiogram import html, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile, FSInputFile

import states
from keyboards import get_start_menu_keyboard
from lexicon.lexicon_ru import LEXICON_BTN_GROUP_LABELS_RU, LEXICON_CHAPTER_LABELS_RU
from middlewares import message_logger
from utils import text_decorator
from utils.message_logger import log_message


async def start(msg: types.Message, state: FSMContext, user: dict) -> None:
    if msg.from_user is None:
        return
    m = [
        f'Привет, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>'
    ]

    await log_message.add_message(await msg.answer("\n".join(m)))
    # intro_file: InputFile = FSInputFile('media/intro/intro_cyrcle.mp4', filename='intro.mp4')
    await log_message.add_message(await msg.answer_video('BAACAgIAAxkDAAMeZaDLZPP06ASnd8ulGRwm_AtepF0AAgtDAAJOEQlJXEw7Z2s-lho0BA',
                           protect_content=True))
    await log_message.add_message(await msg.answer(
        text=LEXICON_BTN_GROUP_LABELS_RU['start_menu'],
        reply_markup=get_start_menu_keyboard(is_admin=user["is_admin"]))
    )
    # print(answer)
    await state.set_state(states.user.UserMainMenu.menu)


async def home(event: types.CallbackQuery | types.Message, state: FSMContext, user: dict) -> None:
    message = event if isinstance(event, types.Message) else event.message

    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(message.chat.id, message)

    await log_message.add_message(await message.answer(
        text=text_decorator.strong(LEXICON_CHAPTER_LABELS_RU['home']))
                                  )
    await log_message.add_message(await message.answer(
        text=LEXICON_BTN_GROUP_LABELS_RU['start_menu'],
        reply_markup=get_start_menu_keyboard(is_admin=user["is_admin"]))
    )

    await state.set_state(states.user.UserMainMenu.menu)
