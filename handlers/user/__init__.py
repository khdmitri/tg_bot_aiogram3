from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command

import states
from filters import ChatTypeFilter, TextFilter
from lexicon.lexicon_ru import LEXICON_BASIC_BTNS_RU
from states.user import UserMainMenu

from . import start, core, practise, lesson


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())
    user_router.message.register(start.home, Command("home"))
    user_router.callback_query.register(start.home, F.data.in_({'practise_exit'}))
    user_router.message.register(start.home, F.text == LEXICON_BASIC_BTNS_RU['back'])
    user_router.callback_query.register(core.user_message_handler, F.data.in_({'user_message'}))
    user_router.callback_query.register(core.view_practises_handler, F.data.in_({'view_practises'}))
    user_router.callback_query.register(practise.view_practise, F.data.startswith('view_practise:'))
    user_router.callback_query.register(lesson.view_lesson, F.data.startswith('view_lesson:'))
    user_router.message.register(core.forward_message_handler, StateFilter(UserMainMenu.message))
    # user_router.message.register(
    #     start.start,
    #     TextFilter("🏠В главное меню"),
    #     StateFilter(states.user.UserMainMenu.menu),
    # )

    return user_router
