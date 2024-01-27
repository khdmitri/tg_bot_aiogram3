from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_INLINE_VIEW_MEDIA_NAV_MENU, LEXICON_DEFAULT_NAMES_RU, \
    LEXICON_ONLINE_PAYMENT_GROUP_RU


class MediaMenuKeyboard:

    def __init__(self, practise_id):
        self.practise_id = practise_id

        self.payment_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['pay'],
            callback_data='lesson_pay_action'
        )

        self.checkout_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['checkout'],
            callback_data='lesson_checkout_action'
        )

        self.payment_online_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback
            )
            for callback, description in LEXICON_ONLINE_PAYMENT_GROUP_RU.items()
        ]

        self.join_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['join_online_lesson'],
            callback_data='media_join_online_lesson'
        )

        self.nav_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback if callback != 'view_practise:' else callback + str(self.practise_id)
            )
            for callback, description in LEXICON_INLINE_VIEW_MEDIA_NAV_MENU.items()
        ]

    def get_back_previous(self):
        kb_builder = InlineKeyboardBuilder()
        return kb_builder.row(*self.nav_buttons, width=1).as_markup()

    def get_payment_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.payment_button]])

    def get_checkout_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.checkout_button]])

    def get_payment_online_keyboard(self):
        kb_builder = InlineKeyboardBuilder()
        return kb_builder.row(*self.payment_online_buttons, width=1).as_markup()

    def get_join_keyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=[[self.join_button]])
