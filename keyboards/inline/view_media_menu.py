from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_INLINE_VIEW_MEDIA_NAV_MENU, LEXICON_DEFAULT_NAMES_RU


class MediaMenuKeyboard:

    def __init__(self, practise_id):
        self.practise_id = practise_id

        self.payment_button = InlineKeyboardButton(
            text=LEXICON_DEFAULT_NAMES_RU['pay'],
            callback_data='lesson_pay_action'
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
