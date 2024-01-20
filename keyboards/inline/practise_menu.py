from typing import Optional, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_INLINE_PRACTISE_MENU_RU, LEXICON_CHAPTER_EXIT_RU, LEXICON_DEFAULT_NAMES_RU, \
    LEXICON_BTN_LABELS_RU, LEXICON_MENU_RU, LEXICON_INLINE_ADMIN_PRACTISE_NAV_MENU
from models.media import Media
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

        self.buttons = self._append_order_buttons(practises)

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
        self.keyboard = kb_builder.row(*self.buttons, width=1).adjust(1, 2, repeat=True)
        kb_builder_extra = InlineKeyboardBuilder()
        self.extra_keyboard = kb_builder_extra.row(*self.extra_buttons, width=1)

    def get_keyboard(self):
        return self.keyboard.as_markup()

    def get_extra_keyboard(self):
        return self.extra_keyboard.as_markup()

    def _append_order_buttons(self, practises: List[Practise]):
        res_list = []
        btn_length = len(self.buttons)
        for i, practise in enumerate(practises):
            res_list.append(self.buttons[i])
            res_list.append(InlineKeyboardButton(
                text='↑',
                callback_data='practise_swap:' + str(practises[i-1].id if i-1 >= 0 else -1) + ":" + str(practise.id)
            ))
            res_list.append(InlineKeyboardButton(
                text='↓',
                callback_data='practise_swap:' + str(practises[i + 1].id if i + 1 < btn_length else -1) + ":" + str(practise.id)
            ))

        return res_list


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

        self.change_publish_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='practise_change_publish'
        )

        self.nav_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_INLINE_ADMIN_PRACTISE_NAV_MENU.items()
        ]

        self.cancel_edit = KeyboardButton(text=LEXICON_BTN_LABELS_RU['cancel_edit'])

    def get_change_title_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_title_button]])

    def get_change_description_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_description_button]])

    def get_change_media_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_media_button]])

    def get_change_publish_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_publish_button]])

    def get_cancel_change_keyboard(self):
        return ReplyKeyboardMarkup(
            keyboard=[[self.cancel_edit]],
            resize_keyboard=True
        )

    def get_back_to_list_keyboard(self):
        kb_builder = InlineKeyboardBuilder()
        return kb_builder.row(*self.nav_buttons, width=1).as_markup()


practise_menu_keyboard = PractiseMenuKeyboard()


class PractiseLessonMenuKeyboard:

    def __init__(self, lessons: Optional[List[Media]] = None):
        if isinstance(lessons, list):
            self.buttons = [
                InlineKeyboardButton(
                    text=lesson.title[:30],
                    callback_data='lesson:' + str(lesson.id)
                )
                for lesson in lessons
            ]
        else:
            self.buttons = []

        self.buttons = self._append_order_buttons(lessons)

        self.buttons.append(InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['add_media'],
            callback_data='add_media'
        ))

        kb_builder = InlineKeyboardBuilder()
        self.keyboard = kb_builder.row(*self.buttons, width=3).adjust(1, 2, repeat=True)

    def get_keyboard(self):
        return self.keyboard.as_markup()

    def _append_order_buttons(self, lessons: List[Media]):
        res_list = []
        btn_length = len(self.buttons)
        for i, lesson in enumerate(lessons):
            res_list.append(self.buttons[i])
            res_list.append(InlineKeyboardButton(
                text='↑',
                callback_data='lesson_swap:' + str(lessons[i-1].id if i-1 >= 0 else -1) + ":" + str(lesson.id)
            ))
            res_list.append(InlineKeyboardButton(
                text='↓',
                callback_data='lesson_swap:' + str(lessons[i + 1].id if i + 1 < btn_length else -1) + ":" + str(lesson.id)
            ))

        return res_list
