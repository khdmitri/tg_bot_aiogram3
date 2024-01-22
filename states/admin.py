from aiogram.fsm.state import State, StatesGroup


class PractiseMenu(StatesGroup):
    home = State()
    new_practise = State()
    edit = State()
    change_title = State()
    change_description = State()
    change_media = State()
    view = State()


class MediaMenu(StatesGroup):
    new = State()
    edit = State()
    change_title = State()
    change_description = State()
    change_media = State()
    change_cost = State()
    change_category = State()
    view = State()


class Page(StatesGroup):
    manage = State()
    new = State()
    edit = State()
    change_name = State()
    change_order = State()
    change_post = State()
    save = State()
