from typing import Optional, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_INLINE_PRACTISE_MENU_RU, LEXICON_CHAPTER_EXIT_RU, LEXICON_DEFAULT_NAMES_RU, \
    LEXICON_BTN_LABELS_RU, LEXICON_MENU_RU
from models.practise import Practise


class PractiseStartMenuKeyboard:

    def __init__(self, practises: Optional[List[Practise]] = None):
        if isinstance(practises, list):
            self.buttons = [
                InlineKeyboardButton(
                    text=practise.title[:30],
                    callback_data='practise:' + str(practise.id)
                )
                for practise in practises
            ]
        else:
            self.buttons = []

        self.extra_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_INLINE_PRACTISE_MENU_RU.items()
        ]

        self.extra_buttons.append(
            InlineKeyboardButton(
                text=LEXICON_CHAPTER_EXIT_RU['practise_exit'],
                callback_data='practise_exit'
            )
        )

        kb_builder = InlineKeyboardBuilder()
        self.keyboard = kb_builder.row(*self.buttons, width=1)
        kb_builder_extra = InlineKeyboardBuilder()
        self.extra_keyboard = kb_builder_extra.row(*self.extra_buttons, width=1)

    def get_keyboard(self):
        return self.keyboard.as_markup()

    def get_extra_keyboard(self):
        return self.extra_keyboard.as_markup()


class PractiseMenuKeyboard:

    def __init__(self):
        self.change_title_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='practise_change_title'
        )

        self.change_description_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='practise_change_description'
        )

        self.change_media_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='practise_change_media'
        )

        self.back_practise_list = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['back_practise_list'],
            callback_data='manage_practises'
        )

        self.delete_practise = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['delete_practise'],
            callback_data='delete_practise'
        )

        self.cancel_edit = KeyboardButton(text=LEXICON_BTN_LABELS_RU['cancel_edit'])

    def get_change_title_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_title_button]])

    def get_change_description_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_description_button]])

    def get_change_media_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_media_button]])

    def get_cancel_change_keyboard(self):
        return ReplyKeyboardMarkup(
            keyboard=[[self.cancel_edit]],
            resize_keyboard=True
        )

    def get_back_to_list_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.back_practise_list]])


practise_menu_keyboard = PractiseMenuKeyboard()
