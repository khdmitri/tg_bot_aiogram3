from aiogram.fsm.state import StatesGroup, State


class GroupMenu(StatesGroup):
    view_lessons = State()
    view_group = State()
    group_message_prompt = State()
