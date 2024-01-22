from aiogram.fsm.state import State, StatesGroup


class UserMainMenu(StatesGroup):
    menu = State()
    message = State()
    view_practises = State()
    about = State()
