from aiogram.fsm.state import State, StatesGroup


class PractiseMenu(StatesGroup):
    home = State()
    new_practise = State()
    edit = State()
    change_title = State()
    change_description = State()
    change_media = State()
