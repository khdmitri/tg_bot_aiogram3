from typing import Optional, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_INLINE_PRACTISE_MENU_RU, LEXICON_CHAPTER_EXIT_RU, LEXICON_DEFAULT_NAMES_RU, \
    LEXICON_BTN_LABELS_RU, LEXICON_MENU_RU, LEXICON_INLINE_ADMIN_PRACTISE_NAV_MENU, LEXICON_INLINE_POST_MENU_RU, \
    LEXICON_INLINE_ADMIN_POST_NAV_MENU
from models.media import Media
from models.post import Post
from models.practise import Practise


class PostMenuKeyboard:

    def __init__(self, posts: Optional[List[Post]] = None):
        if isinstance(posts, list):
            self.buttons = [
                InlineKeyboardButton(
                    text=post.name,
                    callback_data='post:' + str(post.id)
                )
                for post in posts
            ]
        else:
            self.buttons = []

        self.extra_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_INLINE_POST_MENU_RU.items()
        ]

        self.extra_buttons.append(
            InlineKeyboardButton(
                text=LEXICON_CHAPTER_EXIT_RU['post_exit'],
                callback_data='post_exit'
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


class PostEditMenuKeyboard:

    def __init__(self, page: str):
        self.change_name_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='post_change_name'
        )

        self.change_order_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='post_change_order'
        )

        self.change_post_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='post_change_post'
        )

        self.nav_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback + page if callback.startswith('manage_page:') else callback
            )
            for callback, description in LEXICON_INLINE_ADMIN_POST_NAV_MENU.items()
        ]

        self.cancel_edit = KeyboardButton(text=LEXICON_BTN_LABELS_RU['cancel_edit'])

    def get_change_name_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_name_button]])

    def get_change_order_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_order_button]])

    def get_change_post_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_post_button]])

    def get_cancel_change_keyboard(self):
        return ReplyKeyboardMarkup(
            keyboard=[[self.cancel_edit]],
            resize_keyboard=True
        )

    def get_back_to_list_keyboard(self):
        kb_builder = InlineKeyboardBuilder()
        return kb_builder.row(*self.nav_buttons, width=1).as_markup()
