from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter

import states
from filters import ChatTypeFilter, TextFilter

from . import start


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())
    user_router.callback_query.register(start.home, F.data.in_({'practise_exit'}))
    # user_router.message.register(
    #     start.start,
    #     TextFilter("🏠В главное меню"),
    #     StateFilter(states.user.UserMainMenu.menu),
    # )

    return user_router
