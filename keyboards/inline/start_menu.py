from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_MENU_RU, LEXICON_INLINE_MENU_RU, LEXICON_INLINE_ADMIN_MENU_RU


class StartMenuKeyboard:

    def __init__(self, is_admin: bool = False):
        self.buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_INLINE_MENU_RU.items()
        ]

        if is_admin:
            self.buttons += [
                InlineKeyboardButton(
                    text=description,
                    callback_data=callback
                )
                for callback, description in LEXICON_INLINE_ADMIN_MENU_RU.items()
            ]

        kb_builder = InlineKeyboardBuilder()
        self.keyboard = kb_builder.row(*self.buttons, width=1)

    def get_keyboard(self):
        return self.keyboard.as_markup()


def get_start_menu_keyboard(is_admin: bool = False):
    instance = StartMenuKeyboard(is_admin=is_admin)
    return instance.get_keyboard()
