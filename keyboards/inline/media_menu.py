from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder, ReplyKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_DEFAULT_NAMES_RU, LEXICON_INLINE_ADMIN_MEDIA_NAV_MENU, LEXICON_BTN_LABELS_RU, \
    LEXICON_MEDIA_CATEGORIES_RU


class MediaMenuKeyboard:

    def __init__(self, practise_id):
        self.practise_id = practise_id
        self.change_title_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_title'
        )

        self.change_description_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_description'
        )

        self.spam_stream_link_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['send'],
            callback_data='spam_stream_link'
        )

        self.change_stream_link_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_stream_link'
        )

        self.change_category_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_category'
        )

        self.change_media_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_media'
        )

        self.change_action_date_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_action_date'
        )

        self.change_free_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_free'
        )

        self.change_cost_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['change'],
            callback_data='media_change_cost'
        )

        self.nav_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback if callback != 'practise:' else callback + str(self.practise_id)
            )
            for callback, description in LEXICON_INLINE_ADMIN_MEDIA_NAV_MENU.items()
        ]

        self.cancel_edit = KeyboardButton(text=LEXICON_BTN_LABELS_RU['cancel_edit'])

        self.category_buttons = [
            KeyboardButton(
                text=description
            )
            for _, description in LEXICON_MEDIA_CATEGORIES_RU.items()
        ]

        self.category_buttons.append(self.cancel_edit)

        kb_builder = ReplyKeyboardBuilder()
        self.category_keyboard = kb_builder.row(*self.category_buttons, width=3)

    def get_change_title_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_title_button]])

    def get_change_description_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_description_button]])

    def get_spam_stream_link_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.spam_stream_link_button]])

    def get_change_stream_link_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_stream_link_button]])

    def get_change_category_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_category_button]])

    def get_change_media_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_media_button]])

    def get_change_free_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_free_button]])

    def get_change_cost_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_cost_button]])

    def get_change_action_date_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.change_action_date_button]])

    def get_cancel_change_keyboard(self):
        return ReplyKeyboardMarkup(
            keyboard=[[self.cancel_edit]],
            resize_keyboard=True
        )

    def get_category_keyboard(self):
        return self.category_keyboard.as_markup(resize_keyboard=True)

    def get_back_previous(self):
        kb_builder = InlineKeyboardBuilder()
        return kb_builder.row(*self.nav_buttons, width=1).as_markup()
