from typing import Optional, List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_CHAPTER_EXIT_RU, LEXICON_INLINE_VIEW_PRACTISE_NAV_MENU
from models.media import Media
from models.practise import Practise


class ViewPractiseMenuKeyboard:

    def __init__(self, practises: Optional[List[Practise]] = None):
        if isinstance(practises, list):
            self.buttons = [
                InlineKeyboardButton(
                    text=practise.title[:30],
                    callback_data='view_practise:' + str(practise.id)
                )
                for practise in practises
            ]
        else:
            self.buttons = []

        self.extra_buttons = []

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


class PractiseLessonMenuKeyboard:

    def __init__(self, lessons: Optional[List[Media]] = None):
        if isinstance(lessons, list):
            self.buttons = [
                InlineKeyboardButton(
                    text=lesson.title if lesson.is_free else '🔑' + lesson.title,
                    callback_data='view_lesson:' + str(lesson.id)
                )
                for lesson in lessons
            ]
        else:
            self.buttons = []

        self.nav_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_INLINE_VIEW_PRACTISE_NAV_MENU.items()
        ]

        kb_builder = InlineKeyboardBuilder()
        self.keyboard = kb_builder.row(*self.buttons, width=1)

    def get_keyboard(self):
        return self.keyboard.as_markup()

    def get_back_to_list_keyboard(self):
        kb_builder = InlineKeyboardBuilder()
        return kb_builder.row(*self.nav_buttons, width=1).as_markup()
