from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message

from middlewares import message_logger


async def prepare_context(state: FSMContext, new_state: State, message: Message):
    # Изменяем состояние
    await state.set_state(new_state)
    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(message.chat.id, message)
