from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_CHAPTER_EXIT_RU, LEXICON_ADMIN_ONLINE_MENU_RU, LEXICON_BTN_LABELS_RU, \
    LEXICON_ADMIN_ONLINE_MENU_DEEP_RU


class GroupMenuKeyboard:

    def __init__(self):
        self.buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_ADMIN_ONLINE_MENU_RU.items()
        ]

        self.deep_menu_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_ADMIN_ONLINE_MENU_DEEP_RU.items()
        ]

        self.nav_buttons = [
            InlineKeyboardButton(
                text=LEXICON_CHAPTER_EXIT_RU['group_exit'],
                callback_data='group_exit'
            )
        ]

        self.cancel_edit = KeyboardButton(text=LEXICON_BTN_LABELS_RU['cancel_edit'])

        all_buttons = self.buttons + self.nav_buttons

        kb_builder = InlineKeyboardBuilder()
        self.keyboard = kb_builder.row(*all_buttons, width=1)

        all_buttons = self.deep_menu_buttons + self.nav_buttons
        kb_builder = InlineKeyboardBuilder()
        self.deep_keyboard = kb_builder.row(*all_buttons, width=1)

        kb_builder = InlineKeyboardBuilder()
        self.nav_keyboard = kb_builder.row(*self.nav_buttons, width=1)

    def get_keyboard(self):
        return self.keyboard.as_markup()

    def get_deep_keyboard(self):
        return self.deep_keyboard.as_markup()

    def get_nav_keyboard(self):
        return self.nav_keyboard.as_markup()

    def get_cancel_change_keyboard(self):
        return ReplyKeyboardMarkup(
            keyboard=[[self.cancel_edit]],
            resize_keyboard=True
        )


group_menu_keyboard = GroupMenuKeyboard()
